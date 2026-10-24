# Link the payload where Claude Code picks it up
skills="$HOME/.claude/skills"
link="$skills/working-issues"
mkdir -p "$skills"
if [ -e "$link" ] && [ ! -L "$link" ]; then
    echo "$link is a real folder, not a link; move it away first" >&2
    exit 1
fi
ln -sfn "$APP_DIR/skill" "$link"
