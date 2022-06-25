aws-prod () {
    aws-vault exec prod-read-only -- "$@"
}

aws-prod--power-user () {
    aws-vault exec prod-power-user -- "$@"
}

aws-uat () {
    aws-vault exec uat-power-user -- "$@"
}

aws-test () {
    aws-vault exec test-power-user -- "$@"
}

aws-unstable () {
    aws-vault exec unstable-read-only -- "$@"
}
aws-prod-fuzzy () {
    aws-vault exec prod-power-user -- aws-gate session $(aws-vault exec prod-power-user -- aws-fuzzy --ip-only)
}

aws-uat-fuzzy () {
    aws-vault exec uat-power-user -- aws-gate session $(aws-vault exec uat-power-user -- aws-fuzzy --ip-only)
}

aws-test-fuzzy () {
    aws-vault exec test-power-user -- aws-gate session $(aws-vault exec test-power-user -- aws-fuzzy --ip-only)
}

aws-unstable-fuzzy () {
    aws-vault exec unstable-power-user -- aws-gate session $(aws-vault exec unstable-power-user -- aws-fuzzy --ip-only)
}

aws-prod-cli () {
    aws-vault exec prod-read-only -- aws "$@"
}

aws-uat-cli () {
    aws-vault exec uat-read-only -- aws "$@"
}

aws-test-cli () {
    aws-vault exec test-read-only -- aws "$@"
}

aws-unstable-cli () {
    aws-vault exec unstable-read-only -- aws "$@"
}


aws-unstable--admin () {
    aws-vault exec unstable-admin -- "$@"
}

aws-unstable-cli--admin () {
    aws-vault exec unstable-admin -- aws "$@"
}


aws-personal-cli () {
    aws-vault exec personal -- aws "$@"
}

aws-foodbarcodescanner () {
    aws-vault exec foodbarcodescanner -- "$@"
}

aws-foodbarcodescanner-cli () {
    aws-vault exec foodbarcodescanner -- aws "$@"
}


aws-crazyideas () {
    aws-vault exec crazyideas -- "$@"
}

aws-crazyideas-cli () {
    aws-vault exec crazyideas -- aws "$@"
}



# BEGIN functions
flush-dns-cache () {
    sudo killall -HUP mDNSResponder
}
# END functions

#export NVM_DIR="$HOME/.nvm"
#[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" --no-use  # This loads nvm

function init-virtualenvwrapper {
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/work
    source /usr/local/bin/virtualenvwrapper.sh
}


function init-nvm {
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
    if [[ $SHELL == *bash ]]; then
        [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    fi
}

function init-pyenv {
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
}

function init-rvm {
    source $HOME/.rvm/scripts/rvm
}
