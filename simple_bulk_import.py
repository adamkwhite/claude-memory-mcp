#!/usr/bin/env python3
"""
Simple bulk import that writes directly to files without MCP dependencies
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re

def sanitize_filename(title, date):
    """Create a safe filename from title and date"""
    # Extract date part for filename
    date_part = date.split('T')[0] if 'T' in date else date.split(' ')[0]
    
    # Sanitize title
    safe_title = re.sub(r'[^\w\s-]', '', title.lower())
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    safe_title = safe_title.strip('-')[:50]  # Limit length
    
    return f"{date_part}_{safe_title}.md"

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python3 simple_bulk_import.py <batch_file.json>")
        return
    
    batch_file = sys.argv[1]
    
    # Create conversations directory
    conversations_dir = Path("conversations")
    conversations_dir.mkdir(exist_ok=True)
    
    print(f"📂 Reading {batch_file}...")
    
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        
        print(f"✅ Loaded {len(conversations)} conversations")
        
        imported_count = 0
        failed_count = 0
        
        for i, conv in enumerate(conversations):
            try:
                title = conv['title']
                content = conv['content']
                date = conv['date']
                
                # Create filename
                filename = sanitize_filename(title, date)
                filepath = conversations_dir / filename
                
                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                imported_count += 1
                print(f"✅ [{i+1}/{len(conversations)}] {title}")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ [{i+1}/{len(conversations)}] Failed: {e}")
        
        print(f"\n📊 Import Summary:")
        print(f"✅ Successfully imported: {imported_count}")
        print(f"❌ Failed imports: {failed_count}")
        print(f"📁 Files saved to: {conversations_dir}")
        
    except Exception as e:
        print(f"❌ Error reading batch file: {e}")

if __name__ == "__main__":
    main()
