#!/bin/sh
# Claude Code status line - inspired by Powerlevel10k lean style
# Segments: user@host | cwd | git branch | model | context usage

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# user@host
user=$(whoami)
host=$(hostname -s)

# Shorten cwd: replace $HOME with ~
home_dir="$HOME"
short_cwd=$(echo "$cwd" | sed "s|^$home_dir|~|")

# Git branch (skip optional locks to avoid blocking)
git_branch=""
if [ -d "$cwd/.git" ] || git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  git_branch=$(git -C "$cwd" -c core.fsmonitor=false symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" -c core.fsmonitor=false rev-parse --short HEAD 2>/dev/null)
fi

# Context usage indicator
ctx_info=""
if [ -n "$used_pct" ]; then
  used_int=$(printf "%.0f" "$used_pct")
  ctx_info=" | ctx:${used_int}%"
fi

# Git segment
git_seg=""
if [ -n "$git_branch" ]; then
  git_seg=" | \033[0;36m${git_branch}\033[0m"
fi

printf "\033[0;32m%s@%s\033[0m \033[0;33m%s\033[0m%s | \033[0;35m%s\033[0m%s" \
  "$user" "$host" "$short_cwd" "$git_seg" "$model" "$ctx_info"
