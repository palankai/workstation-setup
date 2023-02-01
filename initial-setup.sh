#!/bin/sh

#################################################################
##                                                             ##
##           DO NOT EDIT BY HAND - GENERATED FILE              ##
##                                                             ##
#################################################################

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

function initial_setup {
    log_info "Initialisation"
    ensure_xcode
    ensure_rosetta
    ensure_local_file
    ensure_essentials
    ensure_gpg
    ensure_workstation_repository

    sh $WORKSTATION_INSTALLATION_PATH/setup.d/0*.sh

    restart_gpg
    next_step_instructions
}

function ensure_local_file {
    log_info "Ensure local profile file"
    touch $PROFILE_FILE
    source $PROFILE_FILE

    # SELECT workstation profile
    if ! test_line_exists $PROFILE_FILE "WORKSTATION="; then
        local WORKSTATION=$(menu "Select installation profile" personal maxilux quit)
        if [[ $WORKSTATION == "quit" ]]; then
            echo "bye"
            exit 1
        fi
        echo "export WORKSTATION=$WORKSTATION" >> $PROFILE_FILE
        echo "Selected profile: $WORKSTATION"
    fi
    log_info "Ensure ARCH in local profile"
    ensure_line $PROFILE_FILE "ARCH=" "export ARCH=$(uname -m)"

    log_info "Ensure BREW_HOME in local profile"
    # STORE Brew Home
    if ! test_line_exists $PROFILE_FILE "BREW_HOME="; then
        if [ $(uname -m) = "x86_64" ]; then
            echo "export BREW_HOME=/usr/local" >> $PROFILE_FILE
        else
            echo "export BREW_HOME=/opt/homebrew" >> $PROFILE_FILE
        fi
    fi

    # STORE System Python Path
    ensure_line $PROFILE_FILE "SYSTEM_PYTHON=" "export SYSTEM_PYTHON=/usr/bin/python3"
    ensure_line $PROFILE_FILE "SYSTEM_PIP=" "export SYSTEM_PIP=/usr/bin/pip3"
    ensure_line $PROFILE_FILE "SYSTEM_PYTHON_INSTALL_PATH=" "export SYSTEM_PYTHON_INSTALL_PATH=$(/usr/bin/python3 -m site --user-base)/bin"
    ensure_line $PROFILE_FILE "WORKSTATION_INSTALLATION_PATH=" "export WORKSTATION_INSTALLATION_PATH=$WORKSTATION_INSTALLATION_PATH"

    # LOAD what we have
    source $PROFILE_FILE

    log_result "Env: WORKSTATION=$WORKSTATION"
    log_result "Env: WORKSTATION_INSTALLATION_PATH=$WORKSTATION_INSTALLATION_PATH"
    log_result "Env: ARCH=$ARCH"
    log_result "Env: BREW_HOME=$BREW_HOME"
    log_result "Env: SYSTEM_PYTHON=$SYSTEM_PYTHON"
    log_result "Env: SYSTEM_PIP=$SYSTEM_PIP"
    log_result "Env: SYSTEM_PYTHON_INSTALL_PATH=$SYSTEM_PYTHON_INSTALL_PATH"
}

function ensure_essentials {
    log_info "Installing essentials..."
    if ! is_installed brew; then
        log_info "Installing: brew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        log_result "Brew installed"
    else
        log_info "Updating: brew..."
        brew update
        brew upgrade
        log_result "Brew updated"
    fi
    eval "$($BREW_HOME/bin/brew shellenv)"
    log_info "Homebrew paths setup in this environment"

    brew_install mas

    mkdir -p $HOME/opt/bin
}

function ensure_xcode {
    if type xcode-select >&- && xpath=$( xcode-select --print-path ) && test -d "${xpath}" && test -x "${xpath}" ; then
        log_result "xcode-selected: installed"
    else
        log_info "Installing xcode-select"
        set +e
        xcode-select --install
        set -e
        sleep 3
        read -p "Press [Enter] once the xcode installation is finished..."
        log_result "xcode-selected: installed"
    fi
}

function ensure_rosetta {
    sudo softwareupdate --install-rosetta
}

function ensure_gpg {
    if ! is_installed gpg; then
        brew install gnupg
    fi
    if ! is_installed pinentry-mac; then
        brew install pinentry-mac
    fi
    gpg -k
    mkdir -p ~/.gnupg/
    ensure_line $HOME/.gnupg/gpg-agent.conf pinentry-program "pinentry-program /opt/homebrew/bin/pinentry-mac"

    restart_gpg
    log_result "Initial GPG Setup complete"
}

function ensure_workstation_repository {
    mkdir -p $INSTALLATION_BASE_PATH
    ensure_repository $REPOSITORY $WORKSTATION_INSTALLATION_PATH
}

function next_step_instructions {
    log_br
    log_result "Initial setup completed"
    log_info "Next Steps:"
    log_br
    log_info "cd $WORKSTATION_INSTALLATION_PATH"
    log_info "sh upgrade.sh"
}

function restart_gpg {
    log_info "Restarting GPG..."
    killall gpg-agent || true
    gpg-agent --daemon --homedir $HOME/.gnupg
    export SSH_AUTH_SOCK=$HOME/.gnupg/S.gpg-agent.ssh
    log_result "GPG restarted"
}
export -f restart_gpg

function ensure_repository {
    local url=$1
    local repo_path=$2

    if [ ! -d $repo_path ] ; then
        log_info "Cloning $url into $repo_path..."
        git clone $url $repo_path
        log_result "Repository $url cloned into $repo_path"
    else
        log_info "Updating $url..."
        (cd $repo_path; git pull)
        log_result "Repository $url ($repo_path) updated"
    fi

    log_info "$url Updating submodules..."
    init_submodules $repo_path
    log_result "$url submodules: Updated"
}
export -f ensure_repository

function clone_repository {
    local url=$1
    local repo_path=$2
    local branch=$3

    if [ ! -d $repo_path ] ; then
        log_info "Cloning $url into $repo_path..."
        git clone $url $repo_path
        if [[ -ne "$branch" ]]; then
            git checkout $branch
        fi
        log_result "Repository $url cloned into $repo_path"
    else
        log_info "Updating $url..."
        if [[ -ne "$branch" ]]; then
            git checkout $branch
        fi
        (cd $repo_path; git pull)
        log_result "Repository $url ($repo_path) updated"
    fi
}

function init_submodules {
    local repo_path=${1:-.}
    (cd $repo_path; git submodule update --init --recursive)
    (cd $repo_path; git submodule foreach git checkout master)
    (cd $repo_path; git submodule foreach git pull)
}
export -f init_submodules

function menu {
    PS3="$1: "
    local opts="${@:2}"
    local profile

    select profile in ${opts[@]};
    do
        if [[ ! -z "$profile" && $opts == *"$profile"* ]]; then
            echo $profile
            return 0
        else
            echo "Incorrect selection" >&2
        fi
    done
}
export -f menu

function ensure_line {
    local filename=$1
    local linetest=$2
    local line=$3

    if ! test_line_exists $filename $linetest; then
        echo $line >> $filename
    fi
}
export -f ensure_line

function test_line_exists {
    local fn=$1
    local name=$2
    local res
    local ret

    if test ! -f $fn ; then
        return 1
    fi
    set +e
    res=$(cat $fn | grep "$name" )
    ret=$?
    set -e
    return $ret
}
export -f test_line_exists

function brew_install {
    local package=$1
    if ! is_installed $package; then
        log_info "Installing $package"
        brew install $package
        log_result "$package: installed"
    else
        log_result "$package: nochange"
    fi
}
export -f brew_install

function is_brew_installed {
    local package=$1
    local res
    res=$(brew info --days 0 $package)
    local ret=$?

    if [ "$ret" -ne "0" ]; then
        echo "Not even exists"
        return 1
    fi

    if $(echo $res | grep "Not installed"); then
        echo "Not installed found"
        return 1
    else
        echo "Not installed not found"
        return 0
    fi
}
export -f is_brew_installed

function is_installed {
    local program=$1
    local res
    local ret

    set +e
    res=$(which $program)
    ret=$?
    set -e
    return $ret
}
export -f is_installed

function pip_install {
    local package=$1
    if ! is_pip_installed $package; then
        log_info "Installing $package"
        $SYSTEM_PIP install $package
        log_result "$package: installed"
    else
        log_result "$package: nochange"
    fi
}
export -f pip_install

function is_pip_installed {
    local package=$1
    local ret
    local version
    set +e
    version=$($SYSTEM_PIP freeze | grep $package)
    ret=$?
    set -e
    return $ret
}
export -f is_pip_installed

function log_info {
    echo "$1" >> $LOG_INFO_OUTPUT
}
export -f log_info

function log_br {
    echo "" >> $LOG_INFO_OUTPUT
}
export -f log_br

function log_result {
    echo "$(date '+%Y-%m-%d %H:%M') - $0: $1" >> $LOG_RESULT_OUTPUT
    echo "$1" >> $LOG_INFO_OUTPUT
}
export -f log_result

initial_setup
