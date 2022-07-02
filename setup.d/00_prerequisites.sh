ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/zprofile $HOME/.zprofile

ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/dotfiles/ssh_config $HOME/.ssh/config

ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/gitignore_global $HOME/.gitignore_global
ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/dotfiles/gitconfig $HOME/.gitconfig

mkdir -p $HOME/opt/src
