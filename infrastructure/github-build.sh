#!/usr/bin/env sh
set -e

echo "Using Python: $PYTHON_VERSION"
pyenv global ${PYTHON_VERSION}
pyenv exec python3 --version
pyenv exec pip3 --version

# name: Install packages
echo "Install packages"
apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# name: Install poetry
echo "Install poetry ($POETRY_VERSION)"
pyenv exec pip3 install poetry==$POETRY_VERSION

# name: Cache Poetry virtualenv
echo "Cache Poetry virtualenv"

# name: Set Poetry config
echo "Set Poetry config"
pyenv exec poetry config virtualenvs.in-project false
pyenv exec poetry config virtualenvs.path ~/.virtualenvs

# name: Install Dependencies
echo "Install Dependencies"
pyenv exec poetry install

# name: Lint with flake8
echo "Lint with flake8"
PATH=$PATH:~/.local/bin
pyenv exec poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
pyenv exec poetry run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# name: Test with pytest
echo "Test with pytest"
PATH=$PATH:~/.local/bin
pyenv exec poetry run pytest
