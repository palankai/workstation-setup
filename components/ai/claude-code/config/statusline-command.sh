#!/bin/sh
# Claude Code status line - inspired by Powerlevel10k lean style
# Segments: user@host | cwd | git branch | model | context usage | rate limits | session name

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
session_name=$(echo "$input" | jq -r '.session_name // empty')
effort=$(echo "$input" | jq -r '.effort.level // empty')
five_hour_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
seven_day_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

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

ESC=$(printf '\033')

# Git segment
git_seg=""
if [ -n "$git_branch" ]; then
  git_seg=" | ${ESC}[0;36m${git_branch}${ESC}[0m"
fi

# Context usage indicator
ctx_info=""
if [ -n "$used_pct" ]; then
  used_int=$(printf "%.0f" "$used_pct")
  ctx_info=" | ctx:${used_int}%"
fi

# Rate limits segment (only shown when data is available from Claude.ai subscription)
limits_info=""
if [ -n "$five_hour_pct" ] || [ -n "$seven_day_pct" ]; then
  limits_parts=""
  if [ -n "$five_hour_pct" ]; then
    five_int=$(printf "%.0f" "$five_hour_pct")
    limits_parts="5h:${five_int}%"
  fi
  if [ -n "$seven_day_pct" ]; then
    seven_int=$(printf "%.0f" "$seven_day_pct")
    if [ -n "$limits_parts" ]; then
      limits_parts="${limits_parts} 7d:${seven_int}%"
    else
      limits_parts="7d:${seven_int}%"
    fi
  fi
  limits_info=" | ${ESC}[0;33m${limits_parts}${ESC}[0m"
fi

# Effort level segment (only shown when reasoning effort is active and not default)
effort_info=""
if [ -n "$effort" ] && [ "$effort" != "medium" ]; then
  effort_info=" | ${ESC}[0;34meffort:${effort}${ESC}[0m"
fi

# Session name segment (only shown when a name has been set via /rename)
session_info=""
if [ -n "$session_name" ]; then
  session_info=" | ${ESC}[0;37m${session_name}${ESC}[0m"
fi

printf "\033[0;32m%s@%s\033[0m \033[0;33m%s\033[0m%s | \033[0;35m%s\033[0m%s%s%s%s" \
  "$user" "$host" "$short_cwd" "$git_seg" "$model" "$ctx_info" "$limits_info" "$effort_info" "$session_info"
