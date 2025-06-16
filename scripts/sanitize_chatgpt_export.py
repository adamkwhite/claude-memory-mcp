#!/usr/bin/env python3
"""
Sanitize ChatGPT export by removing private content while preserving structure.

This script removes actual conversation content but keeps the JSON structure
intact for development and testing purposes.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import uuid

def sanitize_message(message: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Sanitize a single message while preserving structure."""
    sanitized = message.copy()
    
    # Replace content with placeholder
    role = message.get("role", "unknown")
    if "content" in sanitized:
        if role == "user":
            sanitized["content"] = f"Sample user message {index + 1}"
        elif role == "assistant":
            sanitized["content"] = f"Sample assistant response {index + 1}"
        else:
            sanitized["content"] = f"Sample {role} message {index + 1}"
    
    # Keep all other fields (id, role, create_time, etc.) unchanged
    return sanitized

def sanitize_chatgpt_conversation(conversation: Dict[str, Any], conv_index: int) -> Dict[str, Any]:
    """Sanitize a ChatGPT conversation while preserving structure."""
    sanitized = conversation.copy()
    
    # Replace title with placeholder
    if "title" in sanitized:
        sanitized["title"] = f"Sample Conversation {conv_index + 1}"
    
    # ChatGPT stores messages in a complex 'mapping' structure
    if "mapping" in sanitized and isinstance(sanitized["mapping"], dict):
        sanitized_mapping = {}
        
        for node_id, node_data in sanitized["mapping"].items():
            sanitized_node = node_data.copy()
            
            # Each node may contain a message
            if "message" in sanitized_node and sanitized_node["message"]:
                message = sanitized_node["message"]
                if isinstance(message, dict) and "content" in message:
                    sanitized_message = message.copy()
                    
                    # Sanitize the content within the message
                    if "content" in sanitized_message and "parts" in sanitized_message["content"]:
                        parts = sanitized_message["content"]["parts"]
                        if isinstance(parts, list) and parts:
                            # Replace content parts with placeholders
                            role = sanitized_message.get("author", {}).get("role", "unknown")
                            if role == "user":
                                sanitized_message["content"]["parts"] = [f"Sample user message from conversation {conv_index + 1}"]
                            elif role == "assistant":
                                sanitized_message["content"]["parts"] = [f"Sample assistant response from conversation {conv_index + 1}"]
                            else:
                                sanitized_message["content"]["parts"] = [f"Sample {role} message from conversation {conv_index + 1}"]
                    
                    sanitized_node["message"] = sanitized_message
            
            sanitized_mapping[node_id] = sanitized_node
        
        sanitized["mapping"] = sanitized_mapping
    
    # Also sanitize any direct messages array if it exists
    if "messages" in sanitized and isinstance(sanitized["messages"], list):
        sanitized["messages"] = [
            sanitize_message(msg, i) 
            for i, msg in enumerate(sanitized["messages"])
        ]
    
    # Keep all metadata fields (id, create_time, update_time, etc.)
    return sanitized

def sanitize_chatgpt_export(input_file: Path, output_file: Path, limit_conversations: int = 5):
    """
    Sanitize ChatGPT export file.
    
    Args:
        input_file: Path to original ChatGPT export
        output_file: Path for sanitized output
        limit_conversations: Maximum conversations to keep (default 5)
    """
    try:
        # Load original export
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different ChatGPT export formats
        if isinstance(data, list):
            # Direct list of conversations
            conversations = data
            print(f"Loaded ChatGPT export with {len(conversations)} conversations")
        elif isinstance(data, dict) and "conversations" in data:
            # Wrapped in conversations object
            conversations = data["conversations"]
            print(f"Loaded ChatGPT export with {len(conversations)} conversations")
        else:
            print("Unknown ChatGPT export format")
            return
        
        # Limit number of conversations for development
        if len(conversations) > limit_conversations:
            conversations = conversations[:limit_conversations]
            print(f"Limited to first {limit_conversations} conversations")
        
        # Sanitize each conversation
        sanitized_conversations = []
        for i, conv in enumerate(conversations):
            try:
                sanitized = sanitize_chatgpt_conversation(conv, i)
                sanitized_conversations.append(sanitized)
            except Exception as e:
                print(f"Error sanitizing conversation {i}: {e}")
                continue
        
        # Preserve original structure
        if isinstance(data, list):
            sanitized_data = sanitized_conversations
        else:
            sanitized_data = data.copy()
            sanitized_data["conversations"] = sanitized_conversations
        
        # Save sanitized export
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sanitized_data, f, indent=2, ensure_ascii=False)
        
        print(f"Sanitized export saved to: {output_file}")
        print(f"Structure preserved with {len(sanitized_conversations)} conversations")
        
        # Print structure summary
        print("\n--- Structure Summary ---")
        if sanitized_conversations:
            sample_conv = sanitized_conversations[0]
            if isinstance(data, list):
                print(f"Root: list of {len(sanitized_conversations)} conversations")
            else:
                print(f"Top-level keys: {list(data.keys())}")
            print(f"Conversation keys: {list(sample_conv.keys())}")
            
            # Show mapping structure if it exists
            if "mapping" in sample_conv:
                mapping = sample_conv["mapping"]
                print(f"Mapping has {len(mapping)} nodes")
                if mapping:
                    sample_node = next(iter(mapping.values()))
                    print(f"Node keys: {list(sample_node.keys())}")
        
    except Exception as e:
        print(f"Error sanitizing export: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python sanitize_chatgpt_export.py <input_file> [output_file] [max_conversations]")
        print("Example: python sanitize_chatgpt_export.py chatgpt_export.json sanitized_export.json 3")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.parent / f"sanitized_{input_file.name}"
    
    max_conversations = 5
    if len(sys.argv) > 3:
        try:
            max_conversations = int(sys.argv[3])
        except ValueError:
            print("Invalid max_conversations value, using default 5")
    
    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        sys.exit(1)
    
    print(f"Sanitizing: {input_file}")
    print(f"Output: {output_file}")
    print(f"Max conversations: {max_conversations}")
    
    sanitize_chatgpt_export(input_file, output_file, max_conversations)

if __name__ == "__main__":
    main()