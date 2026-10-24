# Agentic apps

Skills, mods and plugins for coding agents (Claude Code first), each kept here as its own
application so every machine's profile picks the ones it wants. This guide is all an agent
needs to add or change one; it does not need the rest of the repository.

The repository lives at `$WORKSTATION_INSTALLATION_PATH`, normally `~/opt/workstation-setup`;
this folder is `applications/agentic-apps/` in it.

## How it works

Each folder here is one application. Its install step links its payload into
`~/.claude/skills/<name>`, where Claude Code picks up both plain skills and whole plugins
(mods included). The link points back into this repository, so editing a file here changes
the installed skill or mod at once; nothing is copied. Its uninstall step removes the link.

Which machines get an app is decided by the machine's profile (`profiles/<profile>.yaml`),
not here. Selecting, installing and uninstalling go through `ws`, the repository's manager.

One exception: skills every machine with Claude Code should have, like the `agentic-apps`
skill that points agents at this guide, live in `applications/claude-code/skills/<name>/`
and are linked by Claude Code's own install step. Everything else goes here.

## Kinds and names

| What | App id (= folder name) | `kind` | Payload folder | Linked as |
| --- | --- | --- | --- | --- |
| Skill: a `SKILL.md` with optional scripts and references | `skill-<name>` | `Agent Skill` | `skill/` | `~/.claude/skills/<name>` |
| Mod: a Claude Code plugin with a hooks module (panes, bands, status, tool guards, commands) | `mod-<name>` | `Claude Mod` | `plugin/` | `~/.claude/skills/<name>` |
| Plugin: several skills or mods that are no use apart | `plugin-<name>` | `Claude Plugin` | `plugin/` | `~/.claude/skills/<name>` |

- `<name>` is lowercase words joined by hyphens. For a skill it equals the `name` in its
  `SKILL.md`; for a mod or plugin, the `name` in `.claude-plugin/plugin.json`. The prefix
  keeps app ids apart from ordinary applications (a `skill-git` next to the `git` app).
- One skill or one mod per app. Bundle into a plugin only what can't be used separately,
  so each piece can be switched on per profile.

## Folder layout

```
applications/agentic-apps/skill-<name>/
  README.md          # the application's description (below)
  10-run.sh          # links the payload; runs on every update
  90-uninstall.sh    # removes the link
  skill/             # the payload, linked as ~/.claude/skills/<name>
    SKILL.md
    scripts/ ...     # optional
    references/ ...  # optional
```

A mod or plugin has `plugin/` instead of `skill/`:

```
  plugin/
    .claude-plugin/plugin.json   # { "name": "<name>", "version": "0.1.0", "description": "..." }
    hooks/hooks.json             # { "hooks": {}, "modules": ["./register.tsx"] }
    hooks/register.tsx           # the hooks module
    skills/<skill>/SKILL.md      # a plugin's skills, if it has any
```

Only files directly in the app folder whose names end in `run.sh`, `once.sh`, `uninstall.sh`
or `Brewfile` are steps. Anything in a subfolder is just a file.

## README.md

The frontmatter is what makes the folder an application. Copy, then fill in:

```markdown
---
stereotype: application
id: skill-<name>
name: "<Title>"
kind: Agent Skill
description: "<one line: what it does>"
tags: [agentic, skill]
dependencies: [claude-code]
---

# <Title>

<What it does and when it is used. For a mod: what it shows or changes.>
```

- `kind`: `Agent Skill`, `Claude Mod` or `Claude Plugin`, as in the table.
- `tags`: always `agentic`, then `skill`, `mod` or `plugin`, then any topic tags (`github`,
  `ai`, ...).
- `dependencies`: `claude-code` always; add another application's id only if the skill or
  mod needs that tool installed (for instance `git`).
- Don't add `fundamental`, `order` or other keys unless asked.

## The steps

`10-run.sh` (replace `<name>` and, for a mod or plugin, `skill` with `plugin`):

```bash
# Link the payload where Claude Code picks it up
skills="$HOME/.claude/skills"
link="$skills/<name>"
mkdir -p "$skills"
if [ -e "$link" ] && [ ! -L "$link" ]; then
    echo "$link is a real folder, not a link; move it away first" >&2
    exit 1
fi
ln -sfn "$APP_DIR/skill" "$link"
```

`90-uninstall.sh`:

```bash
link="$HOME/.claude/skills/<name>"
if [ -L "$link" ]; then rm "$link"; fi
```

Steps run with bash, `set -e`, in the app folder, with `APP_DIR` set to it. They run
again on every update, so keep them safe to repeat. The uninstall step removes only a link,
never a real folder.

## Writing the payload

**Skills**: a `SKILL.md` starting with frontmatter:

```markdown
---
name: <name>
description: <what it does and when to use it, with the words a person would use to ask for it>
---
```

then the instructions. The description decides when an agent reaches for the skill, so
include the phrasings that should trigger it. Put long reference material in `references/`
and scripts in `scripts/`, and say in `SKILL.md` when to read or run each.

Keep skills agent-neutral where it costs nothing. `SKILL.md` folders are an open format
other coding agents also read, so the same folder can later be linked into another agent's
skills folder. Write in terms of the task (run the tests, read the file) rather than one
agent's tool names, and keep scripts plain (bash, or Python run with `uv run`).

**Mods** are Claude Code only. The hooks module exports
`register: Register = (on, options) => { ... }`, typed from `'claude-code'`. In Claude Code,
the `plugin-authoring` skill has the API, examples and the type files. Keep `"hooks": {}`
next to `"modules"` in `hooks/hooks.json`: older Claude Code versions refuse the file
without it. Before committing, check the mod:

```bash
claude plugin validate applications/agentic-apps/mod-<name>/plugin
```

Mods need a recent Claude Code; the `claude-code` application runs `claude update` on every
`ws update`. If a mod shows as loaded (`claude plugin list`, as `<name>@skills-dir`) but
does nothing, run `claude update`. A mod's slash command can be tried without a session:
`claude -p "/<command>"`.

## Adding one

1. Create the folder, `README.md`, both steps and the payload as above.
2. Select it in the profile and run its steps (this machine's profile is the default):
   ```bash
   ws select skill-<name>
   ws update skill-<name> --no-deps
   ```
3. Check the link: `ls -l ~/.claude/skills/<name>` points into this folder. For a mod, also
   `claude plugin list` shows `<name>@skills-dir` as loaded.
4. Start a new agent session (or run `/reload-plugins` in Claude Code) to pick it up.
5. Commit the app folder and the profile change. Ask the person before committing.

## Changing one

Edit the payload in place; the installed skill is the same files. A new session (or
`/reload-plugins`) picks up the change. Bump `version` in a mod's `plugin.json` when its
behaviour changes. Renaming `<name>` means changing the link in both steps; run
`ws update skill-<name> --no-deps` afterwards and remove the old link by hand.

## Removing one from a machine

```bash
ws uninstall skill-<name>   # deselects it and marks it for uninstall in the profile
ws update                   # runs the uninstall step
ws uninstall --clear        # takes it off the uninstall list once it succeeded
```

## Bringing in an existing skill

For a skill that already sits as a real folder in `~/.claude/skills/<name>`: create the app
as above, move the folder's contents into `skill/`, delete the now-empty folder, then select
and run the app. The install step refuses to replace a real folder, so nothing is lost by
running it too early.
