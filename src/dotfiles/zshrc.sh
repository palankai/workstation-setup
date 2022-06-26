# Ensure BREW environment variables
eval "$(brew shellenv)"
source ~/.workstation-setup-config


# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH
SHOW_AWS_PROMPT=false

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
# bureau is a cool theme too
ZSH_THEME="ys"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in ~/.oh-my-zsh/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to automatically update without prompting.
# DISABLE_UPDATE_PROMPT="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS=true

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
ZSH_CUSTOM="$HOME/opt/workstation-setup/dotfiles/zsh_custom"

# Which plugins would you like to load?
# Standard plugins can be found in ~/.oh-my-zsh/plugins/*
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git aws)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

export PATH=/usr/local/bin:$PATH
export PATH="$HOMEBREW_PREFIX/opt/curl/bin:$PATH"

# Docker
if [ -f /Applications/Docker.app/Contents/Resources/etc/docker.zsh-completion ]; then
    . /Applications/Docker.app/Contents/Resources/etc/docker.zsh-completion
fi
if [ -f /Applications/Docker.app/Contents/Resources/etc/docker-compose.zsh-completion ]; then
    . /Applications/Docker.app/Contents/Resources/etc/docker-compose.zsh-completion
fi

set -o notify
set -o histexpand

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

# TODO Need to check this on M1
export LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"
#export LDFLAGS="-L/usr/local/opt/curl/lib"
export CPPFLAGS="-I/usr/local/opt/curl/include"
export PKG_CONFIG_PATH="/usr/local/opt/curl/lib/pkgconfig"

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

# GPG Based SSH setup
#gpgconf --launch gpg-agent
#export SSH_AUTH_SOCK=$HOME/.gnupg/S.gpg-agent.ssh

export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"

#export PATH="$PATH:$HOME/opt/anaconda3/bin"

# BEGIN gnu-tools
# TODO make a common directory a move everything there - or link them where they belong
export PATH="$HOME/opt/bin:$HOME/opt/gnubin:$PATH"
export MANPATH="$HOME/opt/gnuman:$MANPATH"
export PATH="$PATH:$HOME/.rvm/bin"
# END gnu-tools


export AWS_FUZZ_USER="csaba.palankai"
export AWS_FUZZ_PRIVATE_IP='True'
export AWS_MIN_TTL=72000
export AWS_VAULT_PROMPT=osascript
export AWS_VAULT_KEYCHAIN_NAME=login

# BEGIN aliases


source $HOME/opt/workstation-setup/src/shell/_functions.sh
source $HOME/opt/workstation-setup/src/sensitive/profiles/$WORKSTATION.sh

# Add RVM to PATH for scripting. Make sure this is the last PATH variable change.

