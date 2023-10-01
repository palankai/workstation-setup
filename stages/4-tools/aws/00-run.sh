mkdir -p $HOME/.aws
chmod 1755 $HOME/.aws

ln -sf $WORKSTATION_INSTALLATION_PATH/sensitive/dotfiles/aws.conf $HOME/.aws/config

# pipx install aws-sam-cli-local
pipx install awscli-local
