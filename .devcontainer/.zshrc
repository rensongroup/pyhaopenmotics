# Show MOTD only once per container session
SESSION_MARKER="/tmp/.motd_shown_$(cat /proc/sys/kernel/random/boot_id 2>/dev/null || echo 'session')"

if [ ! -f "$SESSION_MARKER" ]; then
    # First terminal in this container session
    touch "$SESSION_MARKER"

    # Find workspace directory
    WORKSPACE_DIR=""
    if [ -n "$VSCODE_GIT_IPC_HANDLE" ] || [ -n "$CODESPACES" ]; then
        # We're in VS Code/Codespaces - find workspace
        for dir in /workspaces/* /workspace; do
            if [ -d "$dir" ]; then
                WORKSPACE_DIR="$dir"
                break
            fi
        done
    fi

    # Show MOTD if script exists
    if [ -n "$WORKSPACE_DIR" ] && [ -f "$WORKSPACE_DIR/.devcontainer/motd" ]; then
        "$WORKSPACE_DIR/.devcontainer/motd" 2>/dev/null || true
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
