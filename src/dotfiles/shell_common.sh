source ~/.localenv

# Don't wait for job termination notification
set -o notify

# Don't use ^D to exit
#set -o ignoreeof
if [ $TERM != 'dumb' ]; then
    #allow CTRL-s to go trough
    stty -ixon
fi

# Use case-insensitive filename globbing
# shopt -s nocaseglob

# prevent redirected output from overwriting existing files
# set -o noclobber

# Other env variables ######################
export EDITOR=vim

export HISTSIZE=100000 # bash history will save this many commands
export HISTFILESIZE=${HISTSIZE} # bash will remember this many commands
export HISTCONTROL=ignoredups # ignore duplicate commands
export HISTIGNORE="[   ]*:&:bg:fg:exit" # Ignore some controlling instructions
export HISTTIMEFORMAT="[%Y-%m-%d - %H:%M:%S] " # timestamps

# This for installed openssl by brew; being able to use for compile/build
export LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"

export LESS=-R

if [ $TERM != 'dumb' ]; then
    export LESS_TERMCAP_md=$'\E[01;36m'
fi

# figure out supported ls options

# nice modern GNU 'ls'
if [ "$TERM" != "dumb" ] && [ ls --color >/dev/null 2>&1 ] ; then
    LS_OPTIONS='--color=auto'

# old shitty OSX 'ls'
elif ls --G >/dev/null 2>&1; then
    LS_OPTIONS='-G'

# no known color options supported, use trailing filetype chars instead
else
    LS_OPTIONS='-F'
fi

if ls --group-directories-first >/dev/null 2>&1; then
    LS_OPTIONS="$LS_OPTIONS --group-directories-first"
fi
export LS_OPTIONS

if [ "$TERM" != "dumb" ] && [ hash dircolors 2>/dev/null ]; then
    eval `dircolors -b $HOME/.dircolors`
fi

export PAGER=less
# This option make gpg ask password on terminal
#export GPG_TTY=$(tty)


export LDFLAGS="-L/usr/local/opt/curl/lib"
export CPPFLAGS="-I/usr/local/opt/curl/include"
export PKG_CONFIG_PATH="/usr/local/opt/curl/lib/pkgconfig"

# GPG Based SSH setup
gpgconf --launch gpg-agent
export SSH_AUTH_SOCK=$HOME/.gnupg/S.gpg-agent.ssh


function glog {
    git log --graph --format=format:"%x09%C(yellow)%h%C(reset) %C(green)%ai%x08%x08%x08%x08%x08%x08%C(reset) %C(bold white)%cn%C(reset)%C(auto)%d%C(reset)%n%x09%C(white)%s%C(reset)" --abbrev-commit "$@"
    echo
}

export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"

export PATH="$PATH:$HOME/opt/anaconda3/bin"

# BEGIN gnu-tools
# TODO make a common directory a move everything there - or link them where they belong
PATH="$HOME/opt/bin:$HOME/opt/gnubin:$PATH"
export MANPATH="$HOME/opt/gnuman:$MANPATH"
# END gnu-tools


export AWS_FUZZ_USER="csaba.palankai"
export AWS_FUZZ_PRIVATE_IP='True'
export AWS_MIN_TTL=72000
export AWS_VAULT_PROMPT=osascript
export AWS_VAULT_KEYCHAIN_NAME=login

# BEGIN aliases

alias ll='gls -lAFhG --color=always'
alias emacs='open -a /Applications/Emacs.app'
# END aliases

alias uuid="uuidgen | tr -d '\n' | tr '[:upper:]' '[:lower:]' | pbcopy && pbpaste && echo"
alias UUID="uuidgen | tr -d '\n' | pbcopy && pbpaste && echo"




if [ -e "$HOME/.functions" ]; then
    source $HOME/.functions
fi


if [ -e "$HOME/.generated.sh" ]; then
    source $HOME/.generated.sh
fi

if [ -e "$HOME/.$WORKSTATION.sh" ]; then
    source $HOME/.$WORKSTATION.sh
fi
