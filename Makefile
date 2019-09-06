### <summary>
### Initializes the development/testing environment.
### </summary>
.PHONY: init
init:
	@echo "> Upgrading pip and pipenv..."
	python3 -m pip install --user --upgrade pip pipenv
	python3 -m pipenv install --dev

.PHONY: init.poetry
init.poetry:
	@echo "> Upgrading pip and poetry..."
	python3 -m pip install --user --upgrade pip poetry
	python3 -m poetry install


.PHONY: clean.pyc
clean.pyc:
	@echo "> Cleaning .pyc files..."
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +


### <summary>
### Install the library for local development/use.
### </summary>
.PHONY:install.dev
install.dev:
	pip3 install -e ".[dev]"


### <summary>
### Install the library for local development/use under the user.
### </summary>
.PHONY:install.user
install.user:
	pip3 install --user -e ".[dev]"


lint:
	python3 -m pip install --upgrade flake8
	# stop the build if there are Python syntax errors or undefined names
	python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	python3 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics


### <summary>
### Run tests through pytest.
### </summary>
.PHONY: pytest
pytest: clean.pyc
	python3 -m pipenv run pytest


### <summary>
### Run tests through tox.
### </summary>
.PHONY: test
tox: clean.pyc
	python3 -m pipenv run tox


.PHONY:uninstall.dev
uninstall.dev:
	pip3 uninstall hon

