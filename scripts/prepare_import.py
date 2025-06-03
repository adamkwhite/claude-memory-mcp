#!/usr/bin/env python3
"""
Import your Claude conversations directly using the add_conversation tool
"""

import json
from pathlib import Path

def parse_conversation(conv_data):
    """Parse a single conversation from your format"""
    title = conv_data.get('name', 'Untitled Conversation')
    created_at = conv_data.get('created_at', '')
    chat_messages = conv_data.get('chat_messages', [])
    
    # Build conversation content
    content_parts = []
    content_parts.append(f"# {title}")
    content_parts.append(f"**Date:** {created_at}")
    content_parts.append("")
    
    for msg in chat_messages:
        sender = msg.get('sender', 'unknown')
        text = msg.get('text', '')
        
        if text.strip():
            if sender == 'human':
                content_parts.append(f"**Human**: {text}")
            elif sender == 'assistant':
                content_parts.append(f"**Claude**: {text}")
            else:
                content_parts.append(f"**{sender.title()}**: {text}")
            content_parts.append("")
    
    content = '\n'.join(content_parts)
    
    return {
        'title': title,
        'content': content,
        'date': created_at
    }

def main():
    print("📁 Loading conversations...")
    
    conversations_file = Path("data/conversations.json")
    with open(conversations_file, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    print(f"✅ Loaded {len(conversations)} conversations")
    
    # Parse all conversations
    parsed_conversations = []
    for conv in conversations:
        parsed = parse_conversation(conv)
        parsed_conversations.append(parsed)
    
    # Save parsed conversations for import
    output_file = Path("parsed_conversations.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_conversations, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(parsed_conversations)} parsed conversations to {output_file}")
    print(f"📊 Ready for import!")
    
    # Show sample
    print(f"\n🔍 Sample conversation:")
    print(f"Title: {parsed_conversations[0]['title']}")
    print(f"Content length: {len(parsed_conversations[0]['content'])} characters")
    
    print(f"\n💡 Next step: Use Claude with MCP tools to import these conversations")

if __name__ == "__main__":
    main()
