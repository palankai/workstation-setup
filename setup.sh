source _config.sh
source _setup_functions.sh
source $HOME/.workstation-setup-config
eval "$($BREW_HOME/bin/brew shellenv)"
set -e

if [ "$1" = "ls" ]; then
    for step in setup.d/*.sh; do
        echo "sh setup.sh $(basename $step)"
    done
    exit 0
fi

filter=${1}*.sh
echo "Filter steps: $filter"

for step in setup.d/$filter; do
    log_info "Executing: $step"
    sh $step
done



