export PATH:=~/.local/bin:$(PATH)

### <summary>
### Initializes the development/testing environment.
### </summary>
.PHONY: init
init:
	@echo "PATH is $(PATH)"
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

### <summary>
### Run tests.
### </summary>
.PHONY: test
test: clean.pyc
	pipenv run tox


.PHONY:uninstall.dev
uninstall.dev:
	pip3 uninstall hon

