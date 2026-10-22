"""One-off move from the old setup (components/, targets/<profile>/.upgrade.sh) to the manager.

Idempotent: everything it does is checked first, so running it again, or on a machine
that never had the old setup, changes nothing.
"""

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

from .core import Workspace
from .core.catalog import README, STEP_KINDS, Application, split_frontmatter
from .core.state import State, file_sha256

ONCE_PATTERN = dict(STEP_KINDS)["once"]
BACKUP_SUFFIX = ".pre-migrate"


def migrate(
    workspace: Workspace, state: State, profile: str, home: Path, dry_run: bool
) -> list[str]:
    legacy = legacy_folders(workspace)
    return [
        *seed_once(workspace.root, legacy, state, profile, dry_run),
        *fix_links(workspace.root, legacy, home, dry_run),
    ]


def legacy_folders(workspace: Workspace) -> dict[Path, Application]:
    """Old component folder → application, from the READMEs' `legacy:`."""
    folders = {}
    for application in workspace.catalog():
        meta, _ = split_frontmatter(application.path / README)
        if legacy := meta.get("legacy"):
            folders[workspace.root / legacy] = application
    return folders


def old_lock(root: Path, folder: Path, file: str) -> str:
    """The marker name compile-targets.py gave a once step."""
    parts = ["install", *folder.relative_to(root).parts[1:], file]
    return "_".join(p.replace("-", "_").replace(".", "_") for p in parts)


def seed_once(
    root: Path, legacy: dict[Path, Application], state: State, profile: str, dry_run: bool
) -> Iterator[str]:
    markers = root / "targets" / profile / ".once"
    if not markers.is_dir():
        return
    for old, application in sorted(legacy.items()):
        if not old.is_dir():
            continue
        once_steps = [s.file for s in application.steps if s.kind == "once"]
        for file in sorted(p for p in old.iterdir() if p.is_file() and ONCE_PATTERN.search(p.name)):
            marker = markers / f"installed-{old_lock(root, old, file.name)}-once"
            if not marker.is_file():
                continue
            sha = file_sha256(file)
            same = [s for s in once_steps if file_sha256(application.path / s) == sha]
            step = same[0] if same else once_steps[0] if len(once_steps) == 1 else None
            if step is None:
                yield f"! once {application.id}: no step matches {file.relative_to(root)}"
            elif state.once_record(application.id, step):
                yield f"  once {application.id}/{step}: already recorded"
            else:
                at = datetime.fromtimestamp(marker.stat().st_mtime, UTC).isoformat(timespec="seconds")
                # The old script's hash: if it has changed since, plan flags it instead of rerunning
                if not dry_run:
                    state.record_once(application.id, step, sha, at)
                yield f"+ once {application.id}/{step}: recorded as run at {at}"


def link_candidates(home: Path) -> Iterator[Path]:
    """Where the old steps put links: the home folder, ~/.claude, ~/.config/*, ~/.local/bin."""
    folders = [home, home / ".claude", home / ".local" / "bin"]
    config = home / ".config"
    if config.is_dir():
        folders += [config, *(p for p in config.iterdir() if p.is_dir() and not p.is_symlink())]
    for folder in folders:
        if folder.is_dir():
            yield from sorted(folder.iterdir())


def link_target(link: Path) -> Path:
    return Path(os.path.normpath(link.parent / os.readlink(link)))


def to_new(target: Path, legacy: dict[Path, Application]) -> Path | None:
    for old, application in legacy.items():
        if target.is_relative_to(old):
            return application.path / target.relative_to(old)
    return None


def nested_link(folder: Path, root: Path) -> Path | None:
    """`ln -sf SRC DEST` with DEST a folder (or a link to one) puts the link inside it, as DEST/DEST."""
    inner = folder / folder.name
    if inner.is_symlink() and link_target(inner).is_relative_to(root):
        return inner
    return None


def fix_links(
    root: Path, legacy: dict[Path, Application], home: Path, dry_run: bool
) -> Iterator[str]:
    for path in link_candidates(home):
        if path.is_symlink():
            target = link_target(path)
            if not target.is_relative_to(root):
                continue
            if target.is_dir() and (stray := nested_link(target, root)):
                if not dry_run:
                    stray.unlink()
                yield f"- {stray}: stray link from ln -sf, removed"
            new = to_new(target, legacy)
            if new is None:
                continue
            if not os.path.lexists(new):
                yield f"! {path} -> {target}: no {new}"
                continue
            if not dry_run:
                path.unlink()
                path.symlink_to(new)
            yield f"+ {path}: -> {new}"
        elif path.is_dir() and (inner := nested_link(path, root)):
            # A real folder where a link belongs: every update nests another link into it
            target = link_target(inner)
            new = to_new(target, legacy) or target
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if os.path.lexists(backup):
                yield f"! {path}: a folder where a link to {new} belongs; {backup} already exists"
                continue
            if not dry_run:
                path.rename(backup)
                path.symlink_to(new)
            yield f"+ {path}: folder moved to {backup.name}, linked -> {new}"
