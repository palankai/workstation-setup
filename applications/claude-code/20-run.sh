mkdir -p $HOME/.claude/
ln -sfn $(pwd)/config/hooks ~/.claude/hooks
ln -sf $(pwd)/config/statusline-command.sh ~/.claude/statusline-command.sh
ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/targets/$WORKSTATION/dotfiles/.claude/settings.json $HOME/.claude/settings.json
echo "Claude configuration completed. Hooks and settings have been linked."

# Claude Code's own skills (skills/<name>), on every machine with Claude Code
mkdir -p "$HOME/.claude/skills"
for skill in "$APP_DIR"/skills/*/; do
    name=$(basename "$skill")
    link="$HOME/.claude/skills/$name"
    if [ -e "$link" ] && [ ! -L "$link" ]; then
        echo "$link is a real folder, not a link; move it away first" >&2
        exit 1
    fi
    ln -sfn "${skill%/}" "$link"
done
