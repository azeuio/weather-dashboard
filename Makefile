LOCALES_DIR = locales
LANGUAGES = fr

all: extract update compile

run: install
	python main.py

install:
	pip install -r requirements.txt

help:
	@echo "Makefile for managing translations using Babel."
	@echo "Usage:"
	@echo "  make <command>"
	@echo
	@echo "Available commands:"
	@echo -e "  all\t\t\t- Extract, update, and compile translations"
	@echo -e "  extract\t\t- Extract translatable messages to a .pot file"
	@echo -e "  update\t\t- Update .po files with new messages from the .pot file"
	@echo -e "  compile\t\t- Compile .po files into .mo files"
	@echo -e "  init\t\t\t- Initialize a new language translation"

extract:
	@echo -en "\033[2m"
	pybabel extract -F babel.cfg -o $(LOCALES_DIR)/messages.pot .
	@echo -en "\033[m"

update:
	pybabel update -i $(LOCALES_DIR)/messages.pot -d $(LOCALES_DIR)

compile:
	pybabel compile -d $(LOCALES_DIR)

init:
	eval $(foreach LANGUAGE,$(LANGUAGES), \
		pybabel init -i $(LOCALES_DIR)/messages.pot -d $(LOCALES_DIR) -l ${LANGUAGE} ;)

.PHONY: help extract update compile init