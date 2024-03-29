ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/zprofile $HOME/.zprofile

ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/dotfiles/ssh_config $HOME/.ssh/config

ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/gitignore_global $HOME/.gitignore_global
ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/dotfiles/gitconfig $HOME/.gitconfig


ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/gnupg/gpg-agent.conf $HOME/.gnupg/gpg-agent.conf
ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/gnupg/gpg.conf $HOME/.gnupg/gpg.conf
ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/gnupg/scdaemon.conf $HOME/.gnupg/scdaemon.conf

gpg --recv $KEYID

mkdir -p $HOME/Library/LaunchAgents/

cp $WORKSTATION_INSTALLATION_PATH/templates/homebrew.gpg.gpg-agent.plist $HOME/Library/LaunchAgents/homebrew.gpg.gpg-agent.plist

launchctl load -F $HOME/Library/LaunchAgents/homebrew.gpg.gpg-agent.plist 2>/dev/null
log_result "Homebrew GPG LaunchAgent: installed & started"

cp $WORKSTATION_INSTALLATION_PATH/templates/link-ssh-auth-sock.plist $HOME/Library/LaunchAgents/link-ssh-auth-sock.plist

launchctl load -F $HOME/Library/LaunchAgents/link-ssh-auth-sock.plist 2>/dev/null
log_result "SSH Auth Sock LaunchAgent: installed & started"

