set -e

source _config.sh
source $HOME/.workstation-setup-config
source src/shell/_setup_functions.sh

ln -sf $PWD/src/dotfiles/condarc.yaml $HOME/.condarc

mkdir -p $HOME/.aws
chmod 1755 $HOME/.aws
mkdir -p $HOME/.docker


ln -sf $PWD/src/sensitive/dotfiles/aws.conf $HOME/.aws/config
ln -sf $PWD/src/sensitive/dotfiles/docker-config.json $HOME/.docker/config.json

ln -sf $PWD/src/bin/aws-vault $HOME/opt/bin
