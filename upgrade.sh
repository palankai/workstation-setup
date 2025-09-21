#!/bin/bash

set -e

source "~/.workstation-setup-config"
source "$HOME/opt/workstation-setup/_config.sh"

bash "$WORKSTATION_INSTALLATION_PATH/targets/$WORKSTATION/.upgrade.sh"
