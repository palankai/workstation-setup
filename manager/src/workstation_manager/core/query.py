from collections.abc import Collection
from dataclasses import dataclass, field

from .catalog import Application, Catalog, CatalogError

FLAGS = ("fundamental", "deprecated", "archived", "trial")


@dataclass
class Query:
    """Same filter syntax as the UI search box, but exact ids instead of fuzzy words."""

    ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    kinds: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)

    @property
    def has_filters(self) -> bool:
        return bool(self.tags or self.kinds or self.flags)


def kind_slug(kind: str) -> str:
    return "-".join(kind.lower().split())


def parse_query(terms: list[str]) -> Query:
    query = Query()
    for term in terms:
        lowered = term.lower()
        for prefix, target in (
            ("#", query.tags),
            ("tag:", query.tags),
            ("kind:", query.kinds),
            ("is:", query.flags),
        ):
            if lowered.startswith(prefix):
                value = lowered[len(prefix) :]
                if value:
                    target.append(value)
                break
        else:
            query.ids.append(term)
    for flag in query.flags:
        if flag not in FLAGS:
            raise CatalogError(f"Unknown flag 'is:{flag}', expected one of {', '.join(FLAGS)}")
    return query


def matches(application: Application, query: Query) -> bool:
    return (
        all(any(tag.startswith(t) for tag in application.tags) for t in query.tags)
        and all(kind_slug(application.kind).startswith(k) for k in query.kinds)
        and all(getattr(application, flag) for flag in query.flags)
    )


def select(catalog: Catalog, query: Query, keep: Collection[str] = ()) -> list[str]:
    """Ids named explicitly plus every application matching all filters.

    Archived applications only match filters with `is:archived` or when in `keep`.
    """
    selected = [catalog.get(id).id for id in query.ids]
    if query.has_filters:
        show_archived = "archived" in query.flags
        selected += [
            a.id
            for a in catalog
            if (not a.archived or show_archived or a.id in keep) and matches(a, query)
        ]
    return list(dict.fromkeys(selected))
