export KEYID=0x4C4A8C7E5C4575B7

PROFILE_FILE="$HOME/.workstation-setup-config"
GPG_AGENT_FILE="$HOME/.gnupg/gpg-agent.conf"

LOG_INFO_OUTPUT="/dev/stderr"
LOG_DEBUG_OUTPUT="/dev/stderr"
LOG_RESULT_OUTPUT="workstation-setup-log.txt"

INSTALLATION_BASE_PATH=$HOME/opt

REPOSITORY_NAME=workstation-setup
REPOSITORY=git@github.com:palankai/$REPOSITORY_NAME.git
REPOSITORY_PATH=$INSTALLATION_BASE_PATH/$REPOSITORY_NAME

set -e
