mkdir -p $HOME/.claude/
ln -sf $(pwd)/config/hooks ~/.claude/hooks
ln -sf $(pwd)/config/statusline-command.sh ~/.claude/statusline-command.sh
ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/targets/$WORKSTATION/dotfiles/.claude/settings.json $HOME/.claude/settings.json
echo "Claude configuration completed. Hooks and settings have been linked."
