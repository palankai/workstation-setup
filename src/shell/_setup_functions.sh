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
