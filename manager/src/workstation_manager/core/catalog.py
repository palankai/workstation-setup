import heapq
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ruamel.yaml import YAML, YAMLError

README = "README.md"
FRONTMATTER_DELIMITER = "---"
DEFAULT_ORDER = 100

StepKind = Literal["brewfile", "run", "once"]
STEP_KINDS: tuple[tuple[StepKind, re.Pattern[str]], ...] = (
    ("brewfile", re.compile(r"Brewfile$")),
    ("once", re.compile(r"once\.(sh|py)$")),
    ("run", re.compile(r"run\.(sh|py)$")),
)


class CatalogError(Exception):
    pass


@dataclass(frozen=True)
class Step:
    """An instruction file at the top of an application folder, run in name order."""

    file: str
    kind: StepKind


@dataclass(frozen=True)
class Application:
    id: str
    name: str
    description: str
    tags: tuple[str, ...]
    dependencies: tuple[str, ...]
    homepage: str | None
    # Installed on every profile and can't be deselected
    fundamental: bool
    # Tie-breaker for install order once dependencies are met; lower goes first
    order: int
    steps: tuple[Step, ...]
    path: Path
    body: str


class Catalog:
    def __init__(self, root: Path, applications: Iterable[Application]):
        self.root = root
        self._applications: dict[str, Application] = {}
        for application in applications:
            if application.id in self._applications:
                other = self._applications[application.id].path
                raise CatalogError(
                    f"Duplicate id '{application.id}': {other} and {application.path}"
                )
            self._applications[application.id] = application
        for application in self._applications.values():
            for dependency in application.dependencies:
                if dependency not in self._applications:
                    raise CatalogError(
                        f"'{application.id}' depends on unknown id '{dependency}'"
                    )

    def __iter__(self) -> Iterator[Application]:
        return iter(sorted(self._applications.values(), key=lambda a: a.id))

    def __len__(self) -> int:
        return len(self._applications)

    def __contains__(self, id: object) -> bool:
        return id in self._applications

    @property
    def fundamentals(self) -> list[str]:
        return [a.id for a in self if a.fundamental]

    def get(self, id: str) -> Application:
        try:
            return self._applications[id]
        except KeyError:
            raise CatalogError(f"Unknown application id '{id}'") from None

    def resolve(self, ids: Iterable[str]) -> list[str]:
        """Return ids with their transitive dependencies in install order.

        Dependencies always come first; among the applications whose
        dependencies are met, the lowest order (then id) goes next.
        """
        needed: set[str] = set()
        pending = list(ids)
        while pending:
            id = pending.pop()
            if id not in needed:
                needed.add(id)
                pending.extend(self.get(id).dependencies)

        waiting = {id: set(self.get(id).dependencies) for id in needed}
        dependents: dict[str, list[str]] = {id: [] for id in needed}
        for id, dependencies in waiting.items():
            for dependency in dependencies:
                dependents[dependency].append(id)

        def key(id: str) -> tuple[int, str]:
            return self.get(id).order, id

        ready = [key(id) for id, dependencies in waiting.items() if not dependencies]
        heapq.heapify(ready)
        ordered: list[str] = []
        while ready:
            _, id = heapq.heappop(ready)
            ordered.append(id)
            for dependent in dependents[id]:
                waiting[dependent].discard(id)
                if not waiting[dependent]:
                    heapq.heappush(ready, key(dependent))

        if len(ordered) < len(needed):
            stuck = ", ".join(sorted(needed - set(ordered)))
            raise CatalogError(f"Dependency cycle among: {stuck}")
        return ordered


def load_catalog(root: Path) -> Catalog:
    """Load every application under root; folders can be nested freely."""
    return Catalog(
        root, [load_application(readme) for readme in sorted(root.rglob(README))]
    )


def load_application(readme: Path) -> Application:
    meta, body = split_frontmatter(readme)
    try:
        id = meta["id"]
        name = meta["name"]
    except KeyError as e:
        raise CatalogError(f"{readme}: missing '{e.args[0]}' in frontmatter") from None
    fundamental = meta.get("fundamental", False)
    if not isinstance(fundamental, bool):
        raise CatalogError(f"{readme}: 'fundamental' must be true or false")
    order = meta.get("order", DEFAULT_ORDER)
    if not isinstance(order, int) or isinstance(order, bool):
        raise CatalogError(f"{readme}: 'order' must be an integer")
    return Application(
        id=str(id),
        name=str(name),
        description=str(meta.get("description", "")),
        tags=tuple(str(t) for t in meta.get("tags") or ()),
        dependencies=tuple(str(d) for d in meta.get("dependencies") or ()),
        homepage=meta.get("homepage"),
        fundamental=fundamental,
        order=order,
        steps=find_steps(readme.parent),
        path=readme.parent,
        body=body,
    )


def find_steps(folder: Path) -> tuple[Step, ...]:
    steps = []
    for file in sorted(p for p in folder.iterdir() if p.is_file()):
        for kind, pattern in STEP_KINDS:
            if pattern.search(file.name):
                steps.append(Step(file.name, kind))
                break
    return tuple(steps)


def split_frontmatter(readme: Path) -> tuple[dict, str]:
    lines = readme.read_text().splitlines(keepends=True)
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        raise CatalogError(f"{readme}: missing frontmatter")
    for end, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONTMATTER_DELIMITER:
            break
    else:
        raise CatalogError(f"{readme}: unterminated frontmatter")
    try:
        meta = YAML(typ="safe").load("".join(lines[1:end])) or {}
    except YAMLError as e:
        raise CatalogError(f"{readme}: invalid frontmatter: {e}") from None
    if not isinstance(meta, dict):
        raise CatalogError(f"{readme}: frontmatter must be a mapping")
    return meta, "".join(lines[end + 1 :]).lstrip("\n")
