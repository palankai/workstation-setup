# Clean, simple, compatible and meaningful.
# Tested on Linux, Unix and Windows under ANSI colors.
# It is recommended to use with a dark background.
# Colors: black, red, green, yellow, *blue, magenta, cyan, and white.
#
# Mar 2013 Yad Smood
ZSH_THEME_GIT_PROMPT_UNTRACKED="?"
ZSH_THEME_GIT_PROMPT_ADDED="+"
ZSH_THEME_GIT_PROMPT_MODIFIED="!"
ZSH_THEME_GIT_PROMPT_RENAMED="»"
ZSH_THEME_GIT_PROMPT_DELETED="✘"
ZSH_THEME_GIT_PROMPT_STASHED="$"
ZSH_THEME_GIT_PROMPT_UNMERGED="="
ZSH_THEME_GIT_PROMPT_AHEAD="⇡"
ZSH_THEME_GIT_PROMPT_BEHIND="⇣"
ZSH_THEME_GIT_PROMPT_DIVERGED="⇕"


function git_combined_status() {
  local ref
  if [[ "$(__git_prompt_git config --get oh-my-zsh.hide-status 2>/dev/null)" != "1" ]]; then
    local branch=$(git_current_branch)
    local prompt_status=$(git_prompt_status)
    if [[ -z $prompt_status ]]; then
      local prompt_status="%{$fg_bold[green]%}✓%{$reset_color%}"
    fi
    if [[ ! -z  $branch  ]]; then
      echo "%{$terminfo[bold]$fg[white]%}⎇%{$reset_color%}%{$fg[cyan]%} $branch %{$terminfo[bold]$fg[yellow]%}$prompt_status%{$reset_color%}"
    fi
  fi
}



ZSH_THEME_NVM_PROMPT_PREFIX="%{$fg[green]%} %B⬡%b %{$terminfo[bold]$fg[green]%}"
ZSH_THEME_NVM_PROMPT_SUFFIX="%{$reset_color%}"


SPACESHIP_CONDA_SHOW="${SPACESHIP_CONDA_SHOW=true}"
SPACESHIP_CONDA_PREFIX="${SPACESHIP_CONDA_PREFIX="$SPACESHIP_PROMPT_DEFAULT_PREFIX"}"
SPACESHIP_CONDA_SUFFIX="${SPACESHIP_CONDA_SUFFIX="$SPACESHIP_PROMPT_DEFAULT_SUFFIX"}"
SPACESHIP_CONDA_SYMBOL="${SPACESHIP_CONDA_SYMBOL="🅒 "}"
SPACESHIP_CONDA_COLOR="${SPACESHIP_CONDA_COLOR="%{$fg[blue]%}"}"
SPACESHIP_CONDA_VERBOSE="${SPACESHIP_CONDA_VERBOSE=true}"

# ------------------------------------------------------------------------------
# Section
# ------------------------------------------------------------------------------

spaceship_exists() {
  command -v $1 > /dev/null 2>&1
}

# Show current conda virtual environment
spaceship_conda() {
  [[ $SPACESHIP_CONDA_SHOW == false ]] && return

  # Check if running via conda virtualenv
  spaceship_exists conda && [ -n "$CONDA_DEFAULT_ENV" ] || return

  local conda_env=${CONDA_DEFAULT_ENV}

  if [[ $SPACESHIP_CONDA_VERBOSE == false ]]; then
    conda_env=${CONDA_DEFAULT_ENV:t}
  fi


  echo \
    "$SPACESHIP_CONDA_COLOR" \
    "$SPACESHIP_CONDA_PREFIX" \
    "${SPACESHIP_CONDA_SYMBOL}${conda_env}" \
	"%{$reset_color%}"
}

python_version() {
	local version="$(python3 --version 2>&1)"
	echo " 🐍 %{$terminfo[bold]$fg[blue]%}${version:7}%{$reset_color%}"
}

local exit_code="%(?,%{$terminfo[bold]$fg[green]%}√%{$reset_color%},%{$terminfo[bold]$fg[red]%}✘ %?%{$reset_color%})"

local _nvm_prompt_info='$(nvm_prompt_info)'
local conda_prompt='$(spaceship_conda)'
local _python_version='$(python_version)'
local _git_combined_status='$(git_combined_status)'
local _exit_code='$(last_exit_code)'
local _aws_profile='$(aws_prompt_info)'
local _date='$(date)'

setopt prompt_subst

PROMPT="
$exit_code \
%D{%F %T %Z %A W%V}\
${_aws_profile}\
${conda_prompt}\
${_python_version}\
${_nvm_prompt_info}
%{$terminfo[bold]$fg[white]%}%I%{$reset_color%} %{$terminfo[bold]$fg[yellow]%}%~%{$reset_color%} \
${_git_combined_status}
%{$terminfo[bold]$fg[red]%}$ %{$reset_color%}"
