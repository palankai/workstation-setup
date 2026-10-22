# Runs an application's shell step the way the generated setup scripts did:
# set -e, with the machine config, _config.sh and _setup_functions.sh sourced.
# Usage: bash step.sh <repository> <step file>
set -e
repository="$1"
step="$2"
shift 2

for file in "$HOME/.workstation-setup-config" "$repository/_config.sh" "$repository/_setup_functions.sh"; do
    if [ -f "$file" ]; then
        source "$file"
    fi
done
# _config.sh points this into the current folder; every step's output is captured anyway
export LOG_RESULT_OUTPUT=/dev/null

source "$step"
