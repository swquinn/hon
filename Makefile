.PHONY:install.dev
install.dev:
	pip install -e ".[dev]"

.PHONY: test
test:
	tox

.PHONY:uninstall.dev
uninstall.dev:
	pip uninstall hon