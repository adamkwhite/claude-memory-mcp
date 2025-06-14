#!/usr/bin/env python3
"""
Analyze ChatGPT export structure to understand the format.
"""

import json
import sys
from pathlib import Path

def analyze_structure(data, path="root", max_depth=3, current_depth=0):
    """Recursively analyze JSON structure."""
    if current_depth > max_depth:
        return
    
    indent = "  " * current_depth
    
    if isinstance(data, dict):
        print(f"{indent}{path}: dict with {len(data)} keys")
        for key, value in list(data.items())[:5]:  # Show first 5 keys
            analyze_structure(value, f"{path}.{key}", max_depth, current_depth + 1)
        if len(data) > 5:
            print(f"{indent}  ... and {len(data) - 5} more keys")
            
    elif isinstance(data, list):
        print(f"{indent}{path}: list with {len(data)} items")
        if data:
            print(f"{indent}  Sample item type: {type(data[0]).__name__}")
            if len(data) > 0:
                analyze_structure(data[0], f"{path}[0]", max_depth, current_depth + 1)
            if len(data) > 1:
                print(f"{indent}  ... and {len(data) - 1} more items")
    else:
        value_str = str(data)[:50] + "..." if len(str(data)) > 50 else str(data)
        print(f"{indent}{path}: {type(data).__name__} = {value_str}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_chatgpt_structure.py <chatgpt_export.json>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"File not found: {input_file}")
        sys.exit(1)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"=== ChatGPT Export Structure Analysis ===")
        print(f"File: {input_file}")
        print(f"Root type: {type(data).__name__}")
        print()
        
        analyze_structure(data)
        
        # Additional specific checks
        print(f"\n=== Specific Analysis ===")
        
        if isinstance(data, list):
            print(f"Root is a list with {len(data)} items")
            if data:
                print(f"First item type: {type(data[0]).__name__}")
                if isinstance(data[0], dict):
                    print(f"First item keys: {list(data[0].keys())}")
        
        elif isinstance(data, dict):
            print(f"Root is a dict with keys: {list(data.keys())}")
            
            # Look for conversations
            for key in ['conversations', 'data', 'chats', 'messages']:
                if key in data:
                    conv_data = data[key]
                    print(f"Found '{key}': {type(conv_data).__name__} with {len(conv_data) if isinstance(conv_data, (list, dict)) else 'N/A'} items")
                    
                    if isinstance(conv_data, list) and conv_data:
                        sample = conv_data[0]
                        if isinstance(sample, dict):
                            print(f"  Sample item keys: {list(sample.keys())}")
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    main()