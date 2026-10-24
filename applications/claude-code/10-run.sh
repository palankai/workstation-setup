# Keep the CLI current; the installer puts it in ~/.local/bin, which may not be on PATH yet
claude="$(command -v claude || echo "$HOME/.local/bin/claude")"
"$claude" update
