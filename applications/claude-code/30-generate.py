"""Agent instructions: the shared part here, then the profile's own part from the private repository."""

from workstation_manager.generator import app_file, combine, profile_file

combine(
    "~/.claude/CLAUDE.md",
    app_file("instructions/user.md"),
    profile_file("instructions/user.md", optional=True),
)
combine(
    "~/Workstation/AGENTS.md",
    app_file("instructions/workstation.md"),
    profile_file("instructions/workstation.md", optional=True),
)
