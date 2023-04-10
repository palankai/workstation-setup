source _config.sh
source _setup_functions.sh
source $HOME/.workstation-setup-config
eval "$($BREW_HOME/bin/brew shellenv)"
set -e

if [ "$1" = "ls" ]; then
    list_steps
    exit 0
fi

STEP_FILTER="$1"

run_steps
