#!/bin/bash
# Setup script for Claude Memory MCP Server

set -e

echo "🚀 Setting up Claude Memory MCP Server..."

# Check if we're in WSL/Ubuntu
if [ ! -f /proc/version ] || ! grep -q Microsoft /proc/version; then
    echo "⚠️  This script is designed for WSL/Ubuntu. Proceeding anyway..."
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create target directory
TARGET_DIR="$HOME/claude-memory-mcp"
if [ -d "$TARGET_DIR" ]; then
    echo "📁 Directory $TARGET_DIR already exists. Updating..."
else
    echo "📁 Creating directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

# Copy files
echo "📋 Copying server files..."
cp server.py "$TARGET_DIR/"
cp requirements.txt "$TARGET_DIR/"
cp README.md "$TARGET_DIR/"
cp test_server.py "$TARGET_DIR/"
cp mcp-config.json "$TARGET_DIR/"

# Make scripts executable
chmod +x "$TARGET_DIR/server.py"
chmod +x "$TARGET_DIR/test_server.py"

# Install dependencies
echo "📦 Installing Python dependencies..."
cd "$TARGET_DIR"
pip3 install -r requirements.txt

# Create storage directory
STORAGE_DIR="$HOME/claude-memory"
if [ ! -d "$STORAGE_DIR" ]; then
    echo "🗂️  Creating storage directory: $STORAGE_DIR"
    mkdir -p "$STORAGE_DIR"
fi

# Test the server
echo "🧪 Testing server installation..."
python3 test_server.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Configure Claude Desktop with this MCP server:"
    echo "   Server path: $TARGET_DIR/server.py"
    echo "   Storage path: $STORAGE_DIR"
    echo ""
    echo "2. Add this to your Claude Desktop MCP configuration:"
    echo "   {"
    echo "     \"mcpServers\": {"
    echo "       \"claude-memory\": {"
    echo "         \"command\": \"python3\","
    echo "         \"args\": [\"$TARGET_DIR/server.py\"]"
    echo "       }"
    echo "     }"
    echo "   }"
    echo ""
    echo "3. Restart Claude Desktop"
    echo "4. Test with: search_conversations tool in your next conversation"
    echo ""
    echo "📁 Files installed in: $TARGET_DIR"
    echo "🗂️  Data will be stored in: $STORAGE_DIR"
else
    echo "❌ Setup failed during testing. Check the output above."
    exit 1
fi
