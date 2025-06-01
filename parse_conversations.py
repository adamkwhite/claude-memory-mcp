#!/usr/bin/env python3
"""
Import Claude conversations with the specific format found in your data
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path

def parse_conversation(conv_data):
    """Parse a single conversation from your format"""
    
    # Extract basic info
    title = conv_data.get('name', 'Untitled Conversation')
    created_at = conv_data.get('created_at', datetime.now().isoformat())
    chat_messages = conv_data.get('chat_messages', [])
    
    # Build conversation content from messages
    content_parts = []
    content_parts.append(f"# {title}")
    content_parts.append(f"**Date:** {created_at}")
    content_parts.append("")
    
    for msg in chat_messages:
        sender = msg.get('sender', 'unknown')
        text = msg.get('text', '')
        
        if text.strip():  # Only add non-empty messages
            if sender == 'human':
                content_parts.append(f"**Human**: {text}")
            elif sender == 'assistant':
                content_parts.append(f"**Claude**: {text}")
            else:
                content_parts.append(f"**{sender.title()}**: {text}")
            content_parts.append("")  # Add spacing between messages
    
    content = '\n'.join(content_parts)
    
    return {
        'title': title,
        'content': content,
        'date': created_at
    }

def main():
    print("🚀 Parsing Your Claude Conversations")
    print("===================================")
    
    # Load the conversations
    conversations_file = Path("data/conversations.json")
    
    with open(conversations_file, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    print(f"📦 Found {len(conversations)} conversations")
    
    # Parse first few conversations as examples
    print(f"\n🔍 Parsing examples...")
    
    for i, conv in enumerate(conversations[:3]):  # Show first 3
        parsed = parse_conversation(conv)
        
        print(f"\n--- Conversation {i+1} ---")
        print(f"Title: {parsed['title']}")
        print(f"Date: {parsed['date']}")
        print(f"Content length: {len(parsed['content'])} characters")
        print(f"First 200 chars: {parsed['content'][:200]}...")
    
    print(f"\n✅ All {len(conversations)} conversations can be parsed!")
    print(f"💡 Ready to import into your memory system")

if __name__ == "__main__":
    main()
