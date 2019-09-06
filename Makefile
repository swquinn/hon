### <summary>
### Initializes the development/testing environment.
### </summary>
.PHONY: init
init:
	@echo "PATH is $(PATH)"
	@echo "> Upgrading pip and pipenv..."
	python -m pip install --user --upgrade pip pipenv
	pipenv install --dev


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
	pip3 install --upgrade flake8
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

### <summary>
### Run tests.
### </summary>
.PHONY: test
test: clean.pyc
	pipenv run tox


.PHONY:uninstall.dev
uninstall.dev:
	pip3 uninstall hon

