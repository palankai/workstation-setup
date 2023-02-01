export KEYID=0x4C4A8C7E5C4575B7

export PROFILE_FILE="$HOME/.workstation-setup-config"
export GPG_AGENT_FILE="$HOME/.gnupg/gpg-agent.conf"

export LOG_INFO_OUTPUT="/dev/stderr"
export LOG_DEBUG_OUTPUT="/dev/stderr"

export INSTALLATION_BASE_PATH=$HOME/opt

export REPOSITORY_NAME=workstation-setup
export REPOSITORY=git@github.com:palankai/$REPOSITORY_NAME.git
export REPOSITORY_PATH=$INSTALLATION_BASE_PATH/$REPOSITORY_NAME

export WORKSTATION_INSTALLATION_PATH=$INSTALLATION_BASE_PATH/$REPOSITORY_NAME
export LOG_RESULT_OUTPUT=".workstation-setup-log.txt"

set -e
