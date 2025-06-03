#!/bin/bash
#
# Complete workflow for importing Claude conversations
# This script analyzes the JSON structure then imports the conversations
#

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
CONVERSATIONS_FILE="$DATA_DIR/conversations.json"

echo "🚀 Claude Conversation Import Workflow"
echo "======================================"

# Ensure we're in the right directory
cd "$SCRIPT_DIR"

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run ./setup_environment.sh first"
    exit 1
fi

# Check if conversations.json exists
if [ ! -f "$CONVERSATIONS_FILE" ]; then
    echo "❌ conversations.json not found at: $CONVERSATIONS_FILE"
    echo "💡 Please ensure your exported conversations are at: $CONVERSATIONS_FILE"
    exit 1
fi

echo "📂 Found conversations file: $CONVERSATIONS_FILE"

# Step 1: Analyze JSON structure
echo ""
echo "🔍 Step 1: Analyzing JSON structure..."
echo "--------------------------------------"
python3 "$SCRIPT_DIR/analyze_json.py"

if [ $? -ne 0 ]; then
    echo "❌ JSON analysis failed. Please check the file format."
    exit 1
fi

echo ""
echo "✅ JSON analysis completed successfully!"

# Step 2: Dry run import
echo ""
echo "🔍 Step 2: Dry run import (preview)..."
echo "--------------------------------------"
python3 "$SCRIPT_DIR/bulk_import_enhanced.py" "$CONVERSATIONS_FILE" --dry-run

if [ $? -ne 0 ]; then
    echo "❌ Dry run failed. Please check the errors above."
    exit 1
fi

# Step 3: Confirm actual import
echo ""
echo "🤔 Step 3: Confirmation..."
echo "--------------------------------------"
read -p "Do you want to proceed with the actual import? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Import cancelled by user."
    exit 0
fi

# Step 4: Actual import
echo ""
echo "🚀 Step 4: Importing conversations..."
echo "--------------------------------------"
python3 "$SCRIPT_DIR/bulk_import_enhanced.py" "$CONVERSATIONS_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Import workflow completed successfully!"
    echo ""
    echo "💡 Next steps:"
    echo "   • Test search: search_conversations('python')"
    echo "   • Generate summary: generate_weekly_summary()"
    echo "   • Check specific conversations by topic"
    echo ""
    echo "🔧 Your memory system is ready to use!"
else
    echo "❌ Import failed. Check the errors above."
    exit 1
fi
