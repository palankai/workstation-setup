# Workstation Manager

Selects applications for a profile (`profiles/<name>.yaml`) from the catalog in `applications/`.

- `src/workstation_manager/core` – catalog, profiles and dependency logic; no web dependencies, reusable from a CLI
- `src/workstation_manager/server` – FastAPI JSON API, also serves the built UI
- `ui` – React + TypeScript + Tailwind single-page app

## Run

```sh
ws serve --open    # or: uv run --extra server workstation-manager serve --open
```

The built UI is committed in `ui/dist`, so serving needs no Node. Serves on <http://127.0.0.1:8765>. The repository root is discovered from the current directory; override with `--root`.

## Develop

```sh
uv run workstation-manager serve   # API on :8765 (dev group includes the server extra)
pnpm --dir ui dev                  # UI with hot reload, proxies /api to :8765
uv run pytest
```

After UI changes, run `pnpm --dir ui build` and commit `ui/dist` with the source; builds are deterministic,
so `dist` only changes when the source does.

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

## Update (executor)

`bin/ws` runs the manager from anywhere (symlink it into `~/.local/bin`). The profile comes from `--profile`,
`$WORKSTATION` or `~/.workstation-setup-config`.

```sh
ws plan                      # what update would run
ws update                    # brew update + upgrade, every application's steps, brew cleanup
ws update git '#rust'        # only these (ids, #tag, kind:<kind>, is:<flag>) and their dependencies
ws update --no-brew          # skip brew, including Brewfile steps
ws update fd --force         # also applications the profile doesn't install
ws update jq --no-deps       # without dependencies
ws runs; ws report [RUN]     # past runs; results and failed output
ws once list; ws once reset ID [STEP]
```

A failing application stops its own remaining steps and skips everything depending on it; the rest still runs
(`--fail-fast` stops instead). Brewfile steps run `brew bundle` only when `brew bundle check` fails.
`*.sh` steps run with bash, `*.py` steps with the manager's interpreter, so they can import
`workstation_manager.helpers`. Steps run in their application folder with `APP_ID`, `APP_DIR` and
`WORKSTATION_PROFILE` set.

Machine state lives in `~/.local/state/workstation-setup/` (or `$XDG_STATE_HOME`), never in the repository:
`state.yaml` records once steps (time and sha256 of the script that ran; a changed script is flagged by `plan`,
not rerun), and `runs/<id>/` keeps `run.json` plus every step's full terminal output, also shown in the UI.

## Install order

`dependencies` are hard requirements and always install first. Among applications whose dependencies are met,
the lowest `order` (default `100`, then `id`) goes next. Keep numbers sparse: below 50 for bootstrap,
100 by default, above 200 for late installs.

Inside an application folder, top-level `*Brewfile`, `*run.sh`/`*run.py` (every upgrade) and
`*once.sh`/`*once.py` (first install only) files are the install steps, run in file name order.
