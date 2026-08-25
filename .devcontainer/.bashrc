# shellcheck shell=bash disable=SC2139
# Show MOTD once per container lifecycle (new container or rebuild).
WORKSPACE_DIR=""
if [[ -n "${VSCODE_GIT_IPC_HANDLE:-}" || -n "${CODESPACES:-}" ]]; then
    for dir in /workspaces/* /workspace; do
        if [[ -d "$dir" ]]; then
            WORKSPACE_DIR="$dir"
            break
        fi
    done
fi

if [[ -n "$WORKSPACE_DIR" && -f "$WORKSPACE_DIR/.devcontainer/motd" ]]; then
    HOST_TOKEN="${HOSTNAME:-unknown}"
    MOTD_MARKER_DIR="$HOME/.config/ha-devcontainer"
    MOTD_MARKER_FILE="$MOTD_MARKER_DIR/motd-shown-${HOST_TOKEN}"
    if [[ ! -f "$MOTD_MARKER_FILE" ]]; then
        mkdir -p "$MOTD_MARKER_DIR"
        "$WORKSPACE_DIR/.devcontainer/motd" 2>/dev/null || true
        touch "$MOTD_MARKER_FILE"
    fi
fi

# Find workspace directory for aliases
WORKSPACE_ROOT=""
for dir in /workspaces/* /workspace; do
    if [ -d "$dir" ]; then
        WORKSPACE_ROOT="$dir"
        break
    fi
done

# Change to workspace directory if we're in /home/vscode
if [ "$PWD" = "$HOME" ] && [ -d "/workspaces" ]; then
    cd /workspaces/* 2>/dev/null || true
fi
