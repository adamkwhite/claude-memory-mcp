#!/bin/bash
# Wrapper script to run MCP server with proper environment

# Navigate to project directory
cd /home/adam/Code/claude-memory-mcp

# Add uv to PATH (where it was installed)
export PATH="/home/adam/.local/bin:$PATH"

# Run the server using uv
uv run python server_fastmcp.py
