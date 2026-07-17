#!/usr/bin/env python3
"""
Analyze the structure of conversations.json to understand how to adapt bulk import
"""

import json
from pathlib import Path


def analyze_json_structure(file_path):
    """Analyze the JSON structure and show sample data"""
    try:
        print(f"📁 Analyzing: {file_path}")

        # Get file size
        file_size = Path(file_path).stat().st_size
        print(f"📊 File size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")

        # Read and parse JSON
        with open(file_path, encoding="utf-8") as f:
            # Read first 2000 characters to peek at structure
            f.seek(0)
            sample = f.read(2000)
            print("\n🔍 First 2000 characters:")
            print("-" * 50)
            print(sample)
            print("-" * 50)

            # Reset and try to parse the full JSON
            f.seek(0)
            try:
                data = json.load(f)

                print("\n✅ JSON parsed successfully!")
                print(f"📋 Root type: {type(data).__name__}")

                if isinstance(data, dict):
                    print(f"🔑 Root keys: {list(data.keys())}")

                    # Look for conversations data
                    if "conversations" in data:
                        conversations = data["conversations"]
                        print(f"💬 Found {len(conversations)} conversations")

                        if len(conversations) > 0:
                            print("\n📋 Sample conversation structure:")
                            sample_conv = conversations[0]
                            print(f"   Keys: {list(sample_conv.keys())}")

                            # Show field samples
                            for key, value in sample_conv.items():
                                if isinstance(value, str) and len(value) > 100:
                                    print(f"   {key}: {value[:100]}... (truncated)")
                                else:
                                    print(f"   {key}: {value}")

                elif isinstance(data, list):
                    print(f"📋 Array with {len(data)} items")
                    if len(data) > 0:
                        print(f"🔍 First item type: {type(data[0]).__name__}")
                        if isinstance(data[0], dict):
                            print(f"🔑 First item keys: {list(data[0].keys())}")

                            # Show field samples from first item
                            for key, value in data[0].items():
                                if isinstance(value, str) and len(value) > 100:
                                    print(f"   {key}: {value[:100]}... (truncated)")
                                else:
                                    print(f"   {key}: {value}")

            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print("🔍 This might be a streaming JSON format or malformed")

    except Exception as e:
        print(f"❌ Error analyzing file: {e}")


def main():
    # Use dynamic path resolution to find project data directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"

    # Check what files exist
    print("📂 Files in data directory:")
    for file in data_dir.glob("*.json"):
        file_size = file.stat().st_size
        print(f"   • {file.name} ({file_size:,} bytes)")

    # Focus on conversations.json ONLY
    conversations_file = data_dir / "conversations.json"
    if conversations_file.exists():
        print("\n🎯 ANALYZING CONVERSATIONS.JSON")
        print("=" * 50)
        analyze_json_structure(conversations_file)
    else:
        print(f"❌ conversations.json not found at {conversations_file}")
        print("💡 Available files:")
        for file in data_dir.glob("*.json"):
            print(f"   • {file.name}")
        return

    # Quick check of other files (but don't analyze them fully)
    users_file = data_dir / "users.json"
    if users_file.exists():
        print("\n📋 Note: users.json contains profile data (not conversations)")

    projects_file = data_dir / "projects.json"
    if projects_file.exists():
        print("📋 Note: projects.json contains project data (not conversations)")


if __name__ == "__main__":
    main()
