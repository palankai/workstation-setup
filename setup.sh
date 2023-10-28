source _config.sh
source _setup_functions.sh
source $HOME/.workstation-setup-config
eval "$($BREW_HOME/bin/brew shellenv)"
set -e
export STAGES_ROOT=$PWD/stages

# if [ "$1" = "ls" ]; then
#     list_steps
#     exit 0
# fi

brew update
brew upgrade

run_stages

# STEP_FILTER="$1"

# run_steps
