.DEFAULT_GOAL := all
.PHONY: all compile update Essentials

export PYTHONPATH := ${PWD}/src/pythonlibs

include ~/.workstation-setup-config
export $(shell sed 's/=.*//' ~/.workstation-setup-config)

all: update Essentials
	@echo "System is up-to-date"

update:
	brew update
	brew upgrade
	$(SYSTEM_PYTHON) -m pip install --upgrade pip

Essentials:
	@echo "Ensuring essentials..."
	cd Essentials; brew bundle
	cd Essentials; $(SYSTEM_PIP) install -r requirements.txt
	sh Essentials/dotfiles.sh
	sh Essentials/folders.sh

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


