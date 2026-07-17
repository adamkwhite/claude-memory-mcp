#!/usr/bin/env python3
"""
Automated import using the working memory system
This script processes the parsed conversations and imports them efficiently
"""

import json
import time
import sys
from pathlib import Path

def load_parsed_conversations():
    """Load the parsed conversations"""
    conversations_file = Path("parsed_conversations.json")

    if not conversations_file.exists():
        print("❌ parsed_conversations.json not found")
        print("💡 Run: python3 prepare_import.py first")
        return None

    with open(conversations_file, 'r', encoding='utf-8') as f:
        conversations = json.load(f)

    return conversations

def generate_import_commands(conversations, start_index=3):
    """Generate the import commands for remaining conversations"""

    output_file = Path("import_commands.txt")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Import commands for conversations {start_index+1}-{len(conversations)}\n")
        f.write(f"# Copy and paste these into Claude one at a time\n\n")

        for i in range(start_index, len(conversations)):
            conv = conversations[i]

            # Escape quotes and format for command
            title = conv['title'].replace('"', '\\"')
            date = conv['date']

            # Truncate content if too long (limit for command)
            content = conv['content']
            if len(content) > 8000:  # Reasonable limit for command length
                content = content[:8000] + "\n\n[Content truncated for import]"

            # Escape content
            content = content.replace('"', '\\"').replace('\n', '\\n')

            f.write(f"add_conversation(\"{content}\", \"{title}\", \"{date}\")\n\n")

            # Add progress marker every 10 conversations
            if (i + 1) % 10 == 0:
                f.write(f"# Progress: {i+1}/{len(conversations)} conversations\n\n")

    print(f"📝 Generated import commands in {output_file}")
    return output_file

def create_batch_files(conversations, start_index=3, batch_size=20):
    """Create smaller batch files for easier processing"""

    batch_dir = Path("import_batches")
    batch_dir.mkdir(exist_ok=True)

    total_remaining = len(conversations) - start_index
    num_batches = (total_remaining + batch_size - 1) // batch_size

    print(f"📦 Creating {num_batches} batch files ({batch_size} conversations each)")

    for batch_num in range(num_batches):
        batch_start = start_index + (batch_num * batch_size)
        batch_end = min(batch_start + batch_size, len(conversations))

        batch_file = batch_dir / f"batch_{batch_num+1:02d}.json"

        batch_conversations = conversations[batch_start:batch_end]

        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_conversations, f, indent=2, ensure_ascii=False)

        print(f"   📄 {batch_file}: conversations {batch_start+1}-{batch_end}")

    print(f"\n💡 Import batches created in {batch_dir}/")
    print(f"📋 You can process these batches one at a time")

def main():
    print("🚀 Automated Import Setup")
    print("========================")

    # Load conversations
    conversations = load_parsed_conversations()
    if not conversations:
        return

    print(f"📦 Loaded {len(conversations)} conversations")
    print(f"✅ Already imported: 3 conversations")
    print(f"⏳ Remaining: {len(conversations) - 3} conversations")

    # Create batch files for easier processing
    create_batch_files(conversations, start_index=3, batch_size=20)

    print(f"\n📋 Next steps:")
    print(f"   1. Process batches one at a time using import_batches/")
    print(f"   2. Or continue importing manually conversation by conversation")
    print(f"   3. Each batch contains ~20 conversations for manageable import")

    print(f"\n💡 Progress tracking:")
    print(f"   • Completed: 3/{len(conversations)} ({3/len(conversations)*100:.1f}%)")
    print(f"   • Remaining: {len(conversations)-3} conversations")

if __name__ == "__main__":
    main()
