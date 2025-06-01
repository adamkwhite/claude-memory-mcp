# Makefile for Claude Memory MCP Server

.PHONY: setup test install clean run

# Default target
all: setup test

# Setup the server in Ubuntu/WSL
setup:
	@echo "🚀 Setting up Claude Memory MCP Server..."
	@chmod +x setup.sh
	@./setup.sh

# Test the server installation
test:
	@echo "🧪 Testing server..."
	@python3 test_server.py

# Install dependencies only
install:
	@echo "📦 Installing dependencies..."
	@pip3 install -r requirements.txt

# Clean test files
clean:
	@echo "🧹 Cleaning test files..."
	@rm -rf ~/claude-memory-test

# Run the server (for testing)
run:
	@echo "🏃 Running server..."
	@python3 server.py

# Quick test with sample data
quick-test:
	@echo "⚡ Quick functionality test..."
	@python3 -c "import asyncio; from server import ConversationMemoryServer; server = ConversationMemoryServer('~/claude-memory-test'); print('✅ Server initializes correctly')"

# Show configuration for Claude Desktop
config:
	@echo "📋 Claude Desktop MCP Configuration:"
	@echo "{"
	@echo "  \"mcpServers\": {"
	@echo "    \"claude-memory\": {"
	@echo "      \"command\": \"python3\","
	@echo "      \"args\": [\"$(HOME)/claude-memory-mcp/server.py\"]"
	@echo "    }"
	@echo "  }"
	@echo "}"

# Display help
help:
	@echo "Claude Memory MCP Server - Available Commands:"
	@echo ""
	@echo "  make setup      - Full setup in Ubuntu/WSL"
	@echo "  make test       - Test server functionality"
	@echo "  make install    - Install Python dependencies only"
	@echo "  make run        - Run the server manually"
	@echo "  make clean      - Remove test files"
	@echo "  make config     - Show Claude Desktop configuration"
	@echo "  make help       - Show this help message"
