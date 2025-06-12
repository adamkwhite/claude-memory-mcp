#!/bin/bash
# Wrapper script with dynamic path resolution

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Find uv in PATH or common locations
if command -v uv &> /dev/null; then
    UV_PATH="uv"
elif [ -x "$HOME/.local/bin/uv" ]; then
    UV_PATH="$HOME/.local/bin/uv"
elif [ -x "/usr/local/bin/uv" ]; then
    UV_PATH="/usr/local/bin/uv"
else
    echo "Error: uv command not found in PATH or common locations"
    echo "Please install uv or add it to your PATH"
    exit 1
fi

# Run the server
"$UV_PATH" run python server_fastmcp.py