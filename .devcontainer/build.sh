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

# Install Python dependencies
python3 -m  pip install --upgrade pip

# Install pre-commit hooks
uv tool install prek
uv run prek install

# Install Dependencies
uv sync --all-extras --group dev
