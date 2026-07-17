#!/bin/bash
#
# Troubleshoot import issues and provide solutions
#

echo "🔍 Claude Memory System - Troubleshooting"
echo "========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Current directory: $(pwd)"
echo ""

# Check 1: Virtual environment
echo "1️⃣ Virtual Environment Check"
echo "----------------------------"
if [ -d ".venv" ]; then
    echo "✅ Virtual environment exists"

    if [ -f ".venv/bin/activate" ]; then
        echo "✅ Activation script found"

        # Try to activate and test
        source .venv/bin/activate 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Virtual environment activated successfully"

            # Test MCP import
            if python3 -c "from mcp.server.fastmcp import FastMCP" 2>/dev/null; then
                echo "✅ MCP module available"
            else
                echo "❌ MCP module missing"
                echo "💡 Solution: pip install mcp"
            fi
        else
            echo "❌ Failed to activate virtual environment"
        fi
    else
        echo "❌ Activation script missing"
    fi
else
    echo "❌ Virtual environment not found"
    echo "💡 Solution: python3 -m venv .venv"
fi

echo ""

# Check 2: Data files
echo "2️⃣ Data Files Check"
echo "-------------------"
if [ -d "data" ]; then
    echo "✅ Data directory exists"

    # List all files with sizes
    echo "📊 Files in data directory:"
    for file in data/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "unknown")

            if [ "$size" != "unknown" ] && [ "$size" -gt 0 ]; then
                size_mb=$((size / 1024 / 1024))
                echo "   • $filename: ${size} bytes (${size_mb} MB)"

                # Check if it's conversations.json
                if [ "$filename" = "conversations.json" ]; then
                    if [ "$size" -gt 100000 ]; then  # >100KB suggests real conversation data
                        echo "     ✅ Appears to contain conversation data"
                    else
                        echo "     ⚠️  File is small - might not contain conversations"
                    fi
                fi
            else
                echo "   • $filename: empty or unreadable"
            fi
        fi
    done

    # Specific conversations.json check
    if [ -f "data/conversations.json" ]; then
        echo ""
        echo "🎯 conversations.json analysis:"

        # Check first 200 characters
        first_chars=$(head -c 200 "data/conversations.json" 2>/dev/null)
        if echo "$first_chars" | grep -q '"uuid".*"full_name"'; then
            echo "❌ File contains user profile data, not conversations"
            echo "💡 This is users.json content, not conversation data"
        elif echo "$first_chars" | grep -q '"conversation".*"message"'; then
            echo "✅ File appears to contain conversation data"
        elif echo "$first_chars" | grep -q '\[.*{'; then
            echo "✅ File is JSON array format"
        elif echo "$first_chars" | grep -q '{.*"'; then
            echo "✅ File is JSON object format"
        else
            echo "⚠️  File format unclear from first 200 characters"
        fi

        echo "📝 First 200 characters:"
        echo "$first_chars"
    else
        echo "❌ conversations.json not found"
        echo "💡 Please place your exported Claude conversations in data/conversations.json"
    fi
else
    echo "❌ Data directory not found"
    echo "💡 Solution: mkdir -p data"
fi

echo ""

# Check 3: Server files
echo "3️⃣ Server Files Check"
echo "---------------------"
required_files=("server_fastmcp.py" "main.py" "pyproject.toml")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

echo ""

# Check 4: Python environment
echo "4️⃣ Python Environment Check"
echo "---------------------------"
echo "🐍 Python version: $(python3 --version)"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate 2>/dev/null
    echo "📦 Installed packages:"
    pip list | grep -E "(mcp|fastapi|pydantic)" || echo "   No relevant packages found"
else
    echo "⚠️  Cannot check packages - virtual environment not available"
fi

echo ""

# Solutions summary
echo "🛠️ Quick Fixes"
echo "==============="
echo ""
echo "For environment issues:"
echo "   chmod +x setup_environment.sh"
echo "   ./setup_environment.sh"
echo ""
echo "For missing conversations:"
echo "   • Check if you have the right exported file"
echo "   • Ensure it's named 'conversations.json' in the data/ directory"
echo "   • File should be >100KB and contain conversation content"
echo ""
echo "For import issues:"
echo "   source .venv/bin/activate"
echo "   python3 analyze_json.py"
echo "   python3 bulk_import_enhanced.py data/conversations.json --dry-run"
echo ""
echo "Complete reset:"
echo "   rm -rf .venv"
echo "   ./setup_environment.sh"
echo "   ./import_workflow.sh"
