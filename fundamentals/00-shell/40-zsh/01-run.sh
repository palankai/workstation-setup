
ensure_repository https://github.com/robbyrussell/oh-my-zsh ~/.oh-my-zsh


ensure_zshenv_source
ensure_zprofile_source
ensure_zlogin_source
ensure_zshrc_source

# ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/zshenv $HOME/.zshenv
# ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/zshrc $HOME/.zshrc
ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/p10k.zsh $HOME/.p10k.zsh

echo "Heureka"
