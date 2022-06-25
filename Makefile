.DEFAULT_GOAL := all
.PHONY: all compile

export PYTHONPATH := ${PWD}/src/pythonlibs

include ~/.workstation-setup-config
export $(shell sed 's/=.*//' ~/.workstation-setup-config)

all:
	@echo "Hi all"

python:
	env


compile:
	@echo "Compiling initial-setup.sh"

	@rm -f initial-setup.sh
	@rm -f _initial-setup.sh

	@echo "#!/bin/sh" >> initial-setup.sh
	@echo "#!/bin/sh" >> _initial-setup.sh

	@cat InitialSetup/_config.sh >>initial-setup.sh
	@echo "source ./InitialSetup/_config.sh" >>_initial-setup.sh

	@cat InitialSetup/_functions.sh >>initial-setup.sh
	@echo "source ./InitialSetup/_functions.sh" >>_initial-setup.sh

	@cat InitialSetup/_main.sh >>initial-setup.sh
	@echo "source ./InitialSetup/_main.sh" >>_initial-setup.sh

	@chmod a+x _initial-setup.sh


