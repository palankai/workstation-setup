# https://apple.stackexchange.com/questions/69223/how-to-replace-mac-os-x-utilities-with-gnu-core-utilities

#!/bin/sh
set -e

source _config.sh
source src/shell/_functions.sh

mkdir -p $HOME/opt
mkdir -p $HOME/Projects
mkdir -p $HOME/Local
mkdir -p $HOME/.vim-tmp

mkdir -p $HOME/opt/bin
mkdir -p $HOME/opt/gnubin
mkdir -p $HOME/opt/gnuman
mkdir -p $HOME/opt/gnuman/man1
mkdir -p $HOME/opt/gnuman/man2
mkdir -p $HOME/opt/gnuman/man3
mkdir -p $HOME/opt/gnuman/man4
mkdir -p $HOME/opt/gnuman/man5
mkdir -p $HOME/opt/gnuman/man6
mkdir -p $HOME/opt/gnuman/man7
mkdir -p $HOME/opt/gnuman/man8
mkdir -p $HOME/opt/gnuman/man9
mkdir -p $HOME/opt/gnuman/mann

ensure_repository ~/.oh-my-zsh https://github.com/robbyrussell/oh-my-zsh

ln -sf $PWD/src/sensitive/dotfiles/ssh_config $HOME/.ssh/config

ln -sf $PWD/src/dotfiles/gitignore_global $HOME/.gitignore_global
ln -sf $PWD/src/sensitive/dotfiles/gitconfig $HOME/.gitconfig

ln -sf $PWD/src/dotfiles/tmux.conf $HOME/.tmux.conf
ln -sf $PWD/src/dotfiles/vimrc.vim $HOME/.vimrc

ln -sf $PWD/src/dotfiles/zprofile $HOME/.zprofile
ln -sf $PWD/src/dotfiles/zshrc $HOME/.zshrc
