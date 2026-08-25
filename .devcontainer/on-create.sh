#!/usr/bin/env bash
#
# .devcontainer/on-create.sh - DevContainer On-Create Hook
#
# Runs once when the container is first created, before postCreateCommand.
# Fixes ownership of named Docker volume mount points that Docker initializes
# as root:root so that subsequent scripts (pipx, uv, bootstrap) can write to
# ~/.local and ~/.cache without permission errors.
##

set -e

CYAN='\033[0;36m'
NC='\033[0m'

print_info() {
    echo -e "${CYAN}ℹ $1${NC}" >&2
}

# Load DevContainer environment overrides (.env → .env.local, later wins).
# Makes HA_VERSION and other vars available in this script and user hooks.
# shellcheck source=.devcontainer/_load_env.sh
source "$(cd "$(dirname "$0")" && pwd)/_load_env.sh"

# Fix ownership of named volume mount points.
# Docker creates each volume mount point as root:root when the container starts.
# Volumes are now mounted directly under $HOME (ha-venv and uv-cache) so Docker
# does NOT create ~/.local or ~/.cache as root — VS Code server can write there freely.
print_info "Fixing ownership of Docker volume mount points..."
for _volume_mount in \
    /home/vscode/ha-venv \
    /home/vscode/uv-cache \
    /home/vscode/.claude \
    /home/vscode/.codex \
    /home/vscode/.cache; do
    if [[ -e "$_volume_mount" ]]; then
        sudo chown -R vscode:vscode "$_volume_mount"
    fi
done
unset _volume_mount

# Bootstrap Copilot CLI wrapper/defaults from the repository when present.
# GitHub CLI (and its Copilot CLI command) is provided by devcontainer features;
# this block does NOT install gh or Copilot binaries.
# It only installs project-managed files under ~/.copilot and ~/.local/bin.
# Optional env overrides (from .devcontainer/.env and .env.local):
#   COPILOT_CLI_INSTALL=0                                    -> disable Copilot wrapper/defaults bootstrap block
#   COPILOT_CLI_DEFAULT_FLAGS_SOURCE=/absolute/or/relative   -> custom flags source file
#   COPILOT_CLI_WRAPPER_SOURCE=/absolute/or/relative         -> custom wrapper source file
_copilot_cli_install="${COPILOT_CLI_INSTALL:-1}"

if [[ "$_copilot_cli_install" == "0" ]]; then
    print_info "COPILOT_CLI_INSTALL=0; skipping Copilot CLI defaults and wrapper install."
else
    _copilot_default_flags_rel=".devcontainer/copilot/default-flags.txt"
    _copilot_wrapper_rel=".devcontainer/copilot/copilot-safe"

    _copilot_flags_source="${COPILOT_CLI_DEFAULT_FLAGS_SOURCE:-$_copilot_default_flags_rel}"
    if [[ "$_copilot_flags_source" != /* ]]; then
        _copilot_flags_source="$(pwd)/$_copilot_flags_source"
    fi

    if [[ -f "$_copilot_flags_source" ]]; then
        print_info "Installing Copilot CLI default flags from ${_copilot_flags_source}..."
        mkdir -p /home/vscode/.copilot
        install -m 0644 "$_copilot_flags_source" /home/vscode/.copilot/default-flags.txt
    else
        print_info "No Copilot CLI flags file found at ${_copilot_flags_source}; skipping default flags install."
    fi

    _copilot_wrapper_source="${COPILOT_CLI_WRAPPER_SOURCE:-$_copilot_wrapper_rel}"
    if [[ "$_copilot_wrapper_source" != /* ]]; then
        _copilot_wrapper_source="$(pwd)/$_copilot_wrapper_source"
    fi

    if [[ -f "$_copilot_wrapper_source" ]]; then
        print_info "Installing Copilot CLI wrapper from ${_copilot_wrapper_source}..."
        mkdir -p /home/vscode/.local/bin
        install -m 0755 "$_copilot_wrapper_source" /home/vscode/.local/bin/copilot-safe
    else
        print_info "No Copilot CLI wrapper found at ${_copilot_wrapper_source}; skipping wrapper install."
    fi

    unset _copilot_default_flags_rel
    unset _copilot_wrapper_rel
fi
unset _copilot_flags_source
unset _copilot_wrapper_source
unset _copilot_cli_install
