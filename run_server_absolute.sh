#!/bin/bash
# Wrapper script with absolute UV path

# Navigate to project directory
cd /home/adam/Code/claude-memory-mcp

# Use absolute path to uv (we know it's at /home/adam/.local/bin/uv)
/home/adam/.local/bin/uv run python server_fastmcp.py