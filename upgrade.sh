#!/bin/bash

set -e

source ~/.workstation-setup-config

cd $WORKSTATION_INSTALLATION_PATH/targets/$WORKSTATION/

if [ $# -eq 0 ]; then
    bash .upgrade.sh help
    exit 0
fi


bash .upgrade.sh $1
