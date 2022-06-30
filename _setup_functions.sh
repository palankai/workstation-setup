function initial_setup {
    log_info "Initialisation"
    ensure_xcode
    ensure_local_file
    ensure_essentials
    ensure_gpg
    clone_repository
    gpg_post_setup

    next_step_instructions
}

function ensure_local_file {
    log_info "Ensure local profile file"
    # SELECT workstation profile
    if ! test_line_exists $PROFILE_FILE "WORKSTATION="; then
        local WORKSTATION=$(menu "Select installation profile" personal work quit)
        if [[ $WORKSTATION == "quit" ]]; then
            echo "bye"
            exit 1
        fi
        echo "export WORKSTATION=$WORKSTATION" >> $PROFILE_FILE
        echo "Selected profile: $WORKSTATION"
    fi
    log_info "Ensure ARCH in local profile"
    # STORE Arch
    if ! test_line_exists $PROFILE_FILE "ARCH="; then
        echo "ARCH=$(uname -m)" >> $PROFILE_FILE
    fi
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
    ensure_line $PROFILE_FILE "SYSTEM_PYTHON=" "SYSTEM_PYTHON=/usr/bin/python3"
    ensure_line $PROFILE_FILE "SYSTEM_PIP=" "SYSTEM_PIP=/usr/bin/pip3"
    ensure_line $PROFILE_FILE "SYSTEM_PYTHON_INSTALL_PATH=" "SYSTEM_PYTHON_INSTALL_PATH=$(/usr/bin/python3 -m site --user-base)/bin"
    ensure_line $PROFILE_FILE "WORKSTATION_INSTALLATION_PATH=" "WORKSTATION_INSTALLATION_PATH=$WORKSTATION_INSTALLATION_PATH"

    # LOAD what we have
    source $PROFILE_FILE

    log_result "Env: WORKSTATION=$WORKSTATION"
    log_result "Env: WORKSTATION_INSTALLATION_PATH=$WORKSTATION_INSTALLATION_PATH"
    log_result "Env: ARCH=$ARCH"
    log_result "Env: BREW_HOME=$BREW_HOME"
    log_result "Env: SYSTEM_PYTHON=$SYSTEM_PYTHON"
    log_result "Env: SYSTEM_PIP=$SYSTEM_PIP"
    log_result "Env: SYSTEM_PYTHON_INSTALL_PATH=$SYSTEM_PYTHON_INSTALL_PATH"
    log_result "Env: PYTHONPATH=$PYTHONPATH"
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

function ensure_gpg {
    if ! is_installed gpg; then
        brew install gnupg
    fi
    if ! is_installed pinentry-mac; then
        brew install pinentry-mac
    fi
    gpg -k
    ln -sf $(which pinentry-mac) $HOME/opt/bin/pinentry-mac
    local pinentry_path=$HOME/opt/bin/pinentry-mac
    local target_file=.local_profile
    mkdir -p ~/.gnupg/

    ensure_line $GPG_AGENT_FILE pinentry-program "pinentry-program $pinentry_path"

    ensure_line $PROFILE_FILE "PINENTRY_PATH=" "PINENTRY_PATH=$pinentry_path"
    ensure_line $PROFILE_FILE "GPGCONF_EXEC=" "GPGCONF_EXEC=$(which gpgconf)"

    source $PROFILE_FILE
    log_result "Env: PINENTRY_PATH=$pinentry_path"
    log_result "Env: GPGCONF_EXEC=$GPGCONF_EXEC"

    restart_gpg
    log_result "Initial GPG Setup complete"
}

function clone_repository {
    mkdir -p $INSTALLATION_BASE_PATH
    ensure_repository $REPOSITORY $WORKSTATION_INSTALLATION_PATH
}

function gpg_post_setup {
    ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/gnupg/gpg-agent.conf $HOME/.gnupg/gpg-agent.conf
    ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/gnupg/gpg.conf $HOME/.gnupg/gpg.conf
    ln -sf $WORKSTATION_INSTALLATION_PATH/dotfiles/gnupg/scdaemon.conf $HOME/.gnupg/scdaemon.conf
    log_result "GPG Config files: linked"

    restart_gpg
    mkdir -p $HOME/Library/LaunchAgents/

    local escaped=$(echo $GPGCONF_EXEC | sed 's/\//\\\//g')
    sed "s/{{ GPGCONF_EXEC }}/$escaped/g" $WORKSTATION_INSTALLATION_PATH/templates/homebrew.gpg.gpg-agent.plist >$HOME/Library/LaunchAgents/homebrew.gpg.gpg-agent.plist
    launchctl load -F $HOME/Library/LaunchAgents/homebrew.gpg.gpg-agent.plist 2>/dev/null
    log_result "Homebrew GPG LaunchAgent: installed & started"

    cp $WORKSTATION_INSTALLATION_PATH/templates/link-ssh-auth-sock.plist $HOME/Library/LaunchAgents/link-ssh-auth-sock.plist

    launchctl load -F $HOME/Library/LaunchAgents/link-ssh-auth-sock.plist 2>/dev/null
    log_result "SSH Auth Sock LaunchAgent: installed & started"
}

function next_step_instructions {
    log_br
    log_result "Initial setup completed"
    log_info "Next Steps:"
    log_br
    log_info "cd $WORKSTATION_INSTALLATION_PATH"
    log_info "make"
}

function restart_gpg {
    log_info "Restarting GPG..."
    killall gpg-agent || true
    gpg-agent --daemon --homedir $HOME/.gnupg
    export SSH_AUTH_SOCK=$HOME/.gnupg/S.gpg-agent.ssh
    log_result "GPG restarted"
}

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
    (cd $repo_path; git submodule update --init --recursive)
    (cd $repo_path; git submodule foreach git checkout master)
    (cd $repo_path; git submodule foreach git pull)
    log_result "$url submodules: Updated"
}

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

function ensure_line {
    local filename=$1
    local linetest=$2
    local line=$3

    if ! test_line_exists $filename $linetest; then
        echo $line >> $filename
    fi
}

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

function homebrew_install {
    brew install $@
}
function homebrew_tap {
    brew tap $@
}
function homebrew_cask {
    brew install --cask $@
}

function mas_install {
    local $package_id
    mas install $package_id
}

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

function log_info {
    echo "$1" >> $LOG_INFO_OUTPUT
}
function log_br {
    echo "" >> $LOG_INFO_OUTPUT
}

function log_result {
    echo "$(date '+%Y-%m-%d %H:%M') - $0: $1" >> $LOG_RESULT_OUTPUT
    echo "$1" >> $LOG_INFO_OUTPUT
}

