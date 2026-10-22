# Workstation Manager

Selects applications for a profile (`profiles/<name>.yaml`) from the catalog in `applications/`.

- `src/workstation_manager/core` – catalog, profiles and dependency logic; no web dependencies, reusable from a CLI
- `src/workstation_manager/server` – FastAPI JSON API, also serves the built UI
- `ui` – React + TypeScript + Tailwind single-page app

## Run

```sh
pnpm --dir ui install
pnpm --dir ui build
uv run workstation-manager serve --open
```

Serves on <http://127.0.0.1:8765>. The repository root is discovered from the current directory; override with `--root`.

## Develop

```sh
uv run workstation-manager serve   # API on :8765
pnpm --dir ui dev                  # UI with hot reload, proxies /api to :8765
uv run pytest
```

## Catalog

A folder under `applications/` is an application when its `README.md` frontmatter has `stereotype: application`;
its subfolders aren't searched further. Any other folder (with or without a plain `README.md`) is just for
organising and is searched for more applications. Folders never affect what the UI shows; ids must be unique.

Each application needs `id`, `name` and `kind`. `kind` is a free-text title (`CLI Tool`, `Desktop App`, …);
the list of kinds is whatever the applications declare.

Optional flags (default `false`): `fundamental` (always installed), `deprecated` (badge), `trial` (badge) and
`archived`: kept for reference, hidden from searches unless the query has `is:archived` or the profile would install it.

`applications/settings.yaml` holds catalog-wide settings. `searches` are saved searches shown in the sidebar,
after the built-in `Fundamentals`, `Deprecated`, `Trial` and `Archived`:

```yaml
searches:
  - name: Rust
    query: "#rust"
```

## Search

Each word must match: exact/prefix matches on id and name rank first, then tags and description words,
then fzf-style subsequences (`slvsrch` → `ag-silver-searcher`) and typos (`pyhton`).
`#rust` or `tag:rust` filters by tag, `kind:cli` by kind, `is:fundamental`, `is:deprecated`, `is:archived`, `is:trial` by flag.

## Profiles

Only explicit selections are written, as `$ref` entries pointing at an application `id`.
Applications with `fundamental: true` in their frontmatter are always installed and never written to profiles.
Dependencies declared in an application's frontmatter are resolved at runtime and shown as "required by" in the UI.
Saving keeps comments, blank lines, inline (non-`$ref`) entries and refs to unknown ids untouched.

## Install order

`dependencies` are hard requirements and always install first. Among applications whose dependencies are met,
the lowest `order` (default `100`, then `id`) goes next. Keep numbers sparse: below 50 for bootstrap,
100 by default, above 200 for late installs.

Inside an application folder, top-level `*Brewfile`, `*run.sh`/`*run.py` (every upgrade) and
`*once.sh`/`*once.py` (first install only) files are the install steps, run in file name order.
