#!/bin/sh
set -e

source _config.sh
source $HOME/.workstation-setup-config
source src/shell/_setup_functions.sh

if [ $WORKSTATION == "personal" ]; then
    homebrew_cask "google-drive"
    homebrew_cask "zoom"
    homebrew_cask "slack"

    homebrew_cask "wacom-tablet"
    homebrew_cask "loupedeck"
    homebrew_install "ledger-live"
    homebrew_install "keepassxc"
fi
