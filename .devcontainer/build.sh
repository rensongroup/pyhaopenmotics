#!/usr/bin/env bash

# Stop on errors
set -e

cd "$(dirname "$0")/.."

# Setup venv if not devcontainer of venv is not activated
if [ ! -n "$DEVCONTAINER" ] && [ ! -n "$VIRTUAL_ENV" ];then
  virtualenv .venv
  source .venv/bin/activate
fi

# Install packages
sudo apt update
sudo apt-get upgrade -y

. ${NVM_DIR}/nvm.sh
nvm install
nvm use

npm install

# Install Python dependencies
python3 -m  pip install --upgrade pip

# Install pre-commit hooks
uv tool install prek
uv run prek install
# uv tool install pre-commit --with pre-commit-uv --force-reinstall
# uv run pre-commit install
# uv sync # Install all deps + workspace packages
# uv pip install -r pyproject.toml --extra dev

# Install Dependencies
uv sync --all-extras --group dev
