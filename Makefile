.DEFAULT_GOAL := build
.PHONY: build

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


