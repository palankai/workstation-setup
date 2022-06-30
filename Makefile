.DEFAULT_GOAL := all
.PHONY: all build update brew pip setup

export PYTHONPATH := ${PWD}/src/pythonlibs

include ~/.workstation-setup-config
export $(shell sed 's/=.*//' ~/.workstation-setup-config)

_brew := ${BREW_HOME}/bin/brew

all: update brew pip setup
	@echo "System is up-to-date"

update:
	$(_brew) update
	$(_brew) upgrade
	$(SYSTEM_PYTHON) -m pip install --upgrade pip

brew:
	eval "$($BREW_HOME/bin/brew shellenv)"; cd Setup; $(_brew) bundle

pip:
	$(SYSTEM_PIP) install -r Setup/requirements.txt

setup:
	sh Setup/post-install.sh

build:
	@rm -f initial-setup.sh

	@echo "#!/bin/sh"                                                         >> initial-setup.sh
	@echo ""                                                                  >> initial-setup.sh
	@echo "#################################################################" >> initial-setup.sh
	@echo "##                                                             ##" >> initial-setup.sh
	@echo "##           DO NOT EDIT BY HAND - GENERATED FILE              ##" >> initial-setup.sh
	@echo "##                                                             ##" >> initial-setup.sh
	@echo "#################################################################" >> initial-setup.sh
	@echo ""                                                                  >> initial-setup.sh
	@cat _config.sh                                                           >> initial-setup.sh
	@echo ""                                                                  >> initial-setup.sh
	@cat _setup_functions.sh                                                  >> initial-setup.sh
	@echo ""                                                                  >> initial-setup.sh
	@echo "initial_setup"                                                     >> initial-setup.sh


