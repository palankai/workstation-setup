#!/bin/sh

set -e

source _config.sh
source _setup_functions.sh
source $HOME/.workstation-setup-config

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

mkdir -p $HOME/.aws
chmod 1755 $HOME/.aws
mkdir -p $HOME/.docker

mkdir -p $HOME/Projects
mkdir -p $HOME/Local
mkdir -p $HOME/.vim-tmp

ensure_repository https://github.com/robbyrussell/oh-my-zsh ~/.oh-my-zsh

ln -sf $PWD/src/sensitive/dotfiles/ssh_config $HOME/.ssh/config

ln -sf $PWD/src/dotfiles/gitignore_global $HOME/.gitignore_global
ln -sf $PWD/src/sensitive/dotfiles/gitconfig $HOME/.gitconfig

ln -sf $PWD/src/dotfiles/tmux.conf $HOME/.tmux.conf
ln -sf $PWD/src/dotfiles/vimrc.vim $HOME/.vimrc

ln -sf $PWD/src/dotfiles/zprofile $HOME/.zprofile
ln -sf $PWD/src/dotfiles/zshrc $HOME/.zshrc

ln -sf $PWD/src/dotfiles/condarc.yaml $HOME/.condarc

ln -sf $PWD/src/sensitive/dotfiles/aws.conf $HOME/.aws/config
ln -sf $PWD/src/sensitive/dotfiles/docker-config.json $HOME/.docker/config.json

ln -sf $PWD/src/bin/aws-vault $HOME/opt/bin

# https://apple.stackexchange.com/questions/69223/how-to-replace-mac-os-x-utilities-with-gnu-core-utilities
# https://dev.to/dnsmichi/use-homebrew-bundle-to-manage-software-installation-on-macos-1223

for i in /usr/local/Cellar/*/*/libexec/gnubin; do
    for j in $i/*; do
        ln -sf $j $HOME/opt/gnubin/$(basename $j)
        log_result "$HOME/opt/gnubin/$(basename $j) updated"
    done
done

mans=("man1" "man2" "man3" "man4" "man5" "man6" "man7" "man8" "man9" "mann")

for i in /usr/local/Cellar/*/*/libexec/gnuman; do
    for j in "${mans[@]}"; do
        for k in $i/$j/*; do
            bn=$(basename $k)
            if [ "$bn" != "*" ]; then
                ln -sf $i/$j/$bn $HOME/opt/gnuman/$j/$bn
                log_result "$HOME/opt/gnuman/$j/$bn updated"
            fi
        done
    done
done
