#!/usr/bin/env python3
"""
Simple conversation import using your existing working memory system
No virtual environment dependencies required
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def simple_import():
    """Import conversations using direct file operations (no MCP dependencies)"""

    print("🚀 Simple Conversation Import")
    print("============================")

    # Check the conversations file
    conversations_file = Path("data/conversations.json")

    if not conversations_file.exists():
        print(f"❌ File not found: {conversations_file}")
        return

    # Get file info
    file_size = conversations_file.stat().st_size
    print(f"📂 File: {conversations_file}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")

    # Read and analyze the JSON
    print(f"\n🔍 Analyzing JSON structure...")

    try:
        with open(conversations_file, 'r', encoding='utf-8') as f:
            # Read first 1000 characters to understand structure
            sample = f.read(1000)
            print(f"📝 First 1000 characters:")
            print("-" * 50)
            print(sample)
            print("-" * 50)

            # Reset and parse the JSON
            f.seek(0)
            data = json.load(f)

            print(f"\n✅ JSON parsed successfully!")
            print(f"📋 Root type: {type(data).__name__}")

            if isinstance(data, list):
                print(f"📦 Array with {len(data)} items")
                if len(data) > 0:
                    first_item = data[0]
                    print(f"🔑 First item keys: {list(first_item.keys())}")

                    # Check if this looks like conversation data
                    if any(key in first_item for key in ['content', 'messages', 'conversation', 'text']):
                        print("✅ Looks like conversation data!")
                        print(f"💬 Ready to import {len(data)} conversations")
                    elif 'uuid' in first_item and 'email_address' in first_item:
                        print("⚠️  This appears to be user profile data, not conversations")
                        print("💡 Look for a different file with conversation content")
                    else:
                        print("🤔 Unknown data structure")

            elif isinstance(data, dict):
                print(f"🔑 Object keys: {list(data.keys())}")

                # Look for conversation arrays
                conversation_keys = ['conversations', 'chats', 'messages', 'data']
                found_conversations = None

                for key in conversation_keys:
                    if key in data and isinstance(data[key], list):
                        found_conversations = data[key]
                        print(f"📦 Found {len(found_conversations)} items in '{key}' key")
                        break

                if found_conversations:
                    print(f"💬 Ready to import {len(found_conversations)} conversations")
                else:
                    print("🤔 No conversation arrays found")

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    print(f"\n📋 Analysis complete!")

def check_working_system():
    """Check if the memory system components are available"""

    print("\n🔧 Checking existing system...")

    # Check for key files
    key_files = [
        "server_fastmcp.py",
        "run_server.sh",
        "mcp-config.json"
    ]

    for file in key_files:
        if Path(file).exists():
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")

    # Check if MCP server is running
    print(f"\n💡 To import conversations into your working system:")
    print(f"   1. Ensure MCP server is running: ./run_server.sh")
    print(f"   2. Use Claude with MCP tools to add conversations")
    print(f"   3. Or manually process the JSON data")

if __name__ == "__main__":
    simple_import()
    check_working_system()
