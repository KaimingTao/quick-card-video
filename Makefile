PYTHON ?= python3
VENV_DIR ?= .venv
PIP := $(VENV_DIR)/bin/pip
PY := $(VENV_DIR)/bin/python

.PHONY: init venv install run clean

init: venv install

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip setuptools wheel

install:
	$(PIP) install -r requirements.txt

run:
	$(PY) app.py

clean:
	rm -rf $(VENV_DIR)
