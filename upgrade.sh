#!/bin/bash

set -e

source "~/.workstation-setup-config"

bash "$WORKSTATION_INSTALLATION_PATH/targets/$WORKSTATION/.upgrade.sh"
