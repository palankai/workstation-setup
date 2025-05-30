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

aws-maxilux-prod-cli () {
    aws-vault exec maxilux-prod -- aws "$@"
}
aws-maxilux-prod () {
    aws-vault exec maxilux-prod -- "$@"
}
aws-maxilux-login () {
    aws-vault login maxilux-prod
}


aws-maxilux-uat-cli () {
    aws-vault exec maxilux-uat -- aws "$@"
}
aws-maxilux-uat () {
    aws-vault exec maxilux-uat -- "$@"
}

aws-maxilux-mgmt-cli () {
    aws-vault exec maxilux-mgmt -- aws "$@"
}
aws-maxilux-mgmt () {
    aws-vault exec maxilux-mgmt -- "$@"
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

flush-dns-cache () {
    sudo killall -HUP mDNSResponder
}

flush-dns-cache-50 () {
    for VARIABLE in 1 .. 50
    do
        flush-dns-cache
        sleep 0.1
    done
}

sync-time () {
    sudo sntp -sS pool.ntp.org
}

function swap-yubikey {
    gpg-connect-agent "scd serialno" "learn --force" /bye
}

#export NVM_DIR="$HOME/.nvm"
#[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" --no-use  # This loads nvm

function init-conda() {
    local conda_base
    if [ "$(uname -m)" = "x86_64" ]; then
        conda_base=/usr/local/anaconda3
    else
        conda_base=/opt/homebrew/anaconda3
    fi

    local __conda_setup="$($conda_base/bin/conda 'shell.zsh' 'hook' 2> /dev/null)"

    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "$conda_base/etc/profile.d/conda.sh" ]; then
            . "$conda_base/etc/profile.d/conda.sh"
        else
            export PATH="$conda_base/anaconda3/bin:$PATH"
        fi
    fi
}

function init-rust() {
    source ~/.cargo/env
    export RUST_BACKTRACE=1
}

alias rust_repl=evcxr

function init-ruby {
    export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
    export LDFLAGS="-L/opt/homebrew/opt/ruby/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/ruby/include"
    export PKG_CONFIG_PATH="/opt/homebrew/opt/ruby/lib/pkgconfig"
    export RUBY_CONFIGURE_OPTS="--with-openssl-dir=$(brew --prefix openssl@1.1)"
    eval "$(rbenv init - zsh)"
}


function init-virtualenvwrapper {
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/work
    source /usr/local/bin/virtualenvwrapper.sh
}

function init-nvm {
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
    [ -s "$BREW_HOME/opt/nvm/nvm.sh" ] && \. "$BREW_HOME/opt/nvm/nvm.sh"  # This loads nvm

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

function glog {
    git log --graph --format=format:"%x09%C(yellow)%h%C(reset) %C(green)%ai%x08%x08%x08%x08%x08%x08%C(reset) %C(bold white)%cn%C(reset)%C(auto)%d%C(reset)%n%x09%C(white)%s%C(reset)" --abbrev-commit "$@"
    echo
}

function restart-gpg {
    gpgconf --kill gpg-agent
    export GPG_TTY=$(tty)
    # GPG Based SSH setup
    gpgconf --launch gpg-agent
    export SSH_AUTH_SOCK=$HOME/.gnupg/S.gpg-agent.ssh
}

alias ll='ls -lAFhG --color=always'
alias emacs='open -a /Applications/Emacs.app'
# END aliases

alias uuid="uuidgen | tr -d '\n' | tr '[:upper:]' '[:lower:]' | pbcopy && pbpaste && echo"
alias UUID="uuidgen | tr -d '\n' | pbcopy && pbpaste && echo"


