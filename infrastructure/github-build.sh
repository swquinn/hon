#!/usr/bin/env sh
set -e


### <summary>
### Run the dependency installation job.
### <summary>
echo
echo
echo "Install dependencies"
echo "> Installing and upgrading pip, pipenv..."
PATH=$PATH:/root/.local/bin
make init


### <summary>
### Run the linting job.
### <summary>
echo
echo
echo "Lint with flake8"
PATH=$PATH:/root/.local/bin
make lint


### <summary>
### Run the test job.
### <summary>
echo
echo
echo "Test with pytest"
PATH=$PATH:/root/.local/bin
make pytest
