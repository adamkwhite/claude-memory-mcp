#!/usr/bin/env python3

# Add src directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
"""
Enhanced Bulk Conversation Import Script for Claude Memory System
Handles Claude conversation exports and provides detailed progress tracking
"""

import os
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import asyncio
import argparse
from typing import Dict, List, Any, Optional
import re

# Add the MCP server path
sys.path.append('/home/adam/Code/claude-memory-mcp')
from server_fastmcp import ConversationMemoryServer

class EnhancedBulkImporter:
    def __init__(self, dry_run: bool = False):
        self.memory_server = ConversationMemoryServer() if not dry_run else None
        self.imported_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.errors = []
        self.dry_run = dry_run
        self.conversation_titles = set()  # Track titles to avoid duplicates
    
    def extract_conversation_content(self, conversation: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract content, title, and date from various conversation formats"""
        
        # Common fields to check for content
        content_fields = ['content', 'text', 'body', 'conversation', 'messages']
        title_fields = ['title', 'name', 'subject', 'conversation_title']
        date_fields = ['date', 'created_at', 'timestamp', 'created', 'date_created']
        
        # Extract content
        content = None
        for field in content_fields:
            if field in conversation and conversation[field]:
                content = conversation[field]
                break
        
        # If content is a list (like messages), join them
        if isinstance(content, list):
            if len(content) > 0 and isinstance(content[0], dict):
                # Handle message format: [{"role": "user", "content": "..."}, ...]
                content_parts = []
                for msg in content:
                    role = msg.get('role', msg.get('sender', 'unknown'))
                    text = msg.get('content', msg.get('text', msg.get('message', '')))
                    content_parts.append(f"**{role.title()}**: {text}")
                content = '\n\n'.join(content_parts)
            else:
                # Simple list of strings
                content = '\n\n'.join(str(item) for item in content)
        
        if not content:
            return None
        
        # Extract title
        title = None
        for field in title_fields:
            if field in conversation and conversation[field]:
                title = str(conversation[field]).strip()
                break
        
        # Generate title from content if not found
        if not title:
            # Extract first meaningful line or sentence
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 10 and not line.startswith('**'):
                    title = line[:80] + "..." if len(line) > 80 else line
                    break
            
            if not title:
                title = f"Conversation {self.imported_count + 1}"
        
        # Extract date
        date_str = None
        for field in date_fields:
            if field in conversation and conversation[field]:
                date_str = conversation[field]
                break
        
        # Parse and normalize date
        if date_str:
            try:
                # Handle various date formats
                if isinstance(date_str, (int, float)):
                    # Unix timestamp
                    date_str = datetime.fromtimestamp(date_str, tz=timezone.utc).isoformat()
                elif isinstance(date_str, str):
                    # Try to parse ISO format or convert other formats
                    try:
                        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date_str = parsed_date.isoformat()
                    except:
                        # Try other common formats
                        try:
                            parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            date_str = parsed_date.isoformat()
                        except:
                            # Keep original if can't parse
                            pass
            except:
                date_str = None
        
        # Use current time if no date found
        if not date_str:
            date_str = datetime.now(timezone.utc).isoformat()
        
        return {
            'content': content,
            'title': title,
            'date': date_str
        }
    
    def generate_unique_title(self, base_title: str) -> str:
        """Generate a unique title by adding a number if needed"""
        original_title = base_title
        counter = 1
        
        while base_title in self.conversation_titles:
            base_title = f"{original_title} ({counter})"
            counter += 1
        
        self.conversation_titles.add(base_title)
        return base_title
    
    async def import_conversation(self, conversation_data: Dict[str, str]) -> bool:
        """Import a single conversation"""
        try:
            title = self.generate_unique_title(conversation_data['title'])
            content = conversation_data['content']
            date = conversation_data['date']
            
            if self.dry_run:
                print(f"🔍 [DRY RUN] Would import: {title[:60]}...")
                print(f"   📅 Date: {date}")
                print(f"   📝 Content length: {len(content)} characters")
                self.imported_count += 1
                return True
            
            result = await self.memory_server.add_conversation(content, title, date)
            
            if result.get('status') == 'success':
                self.imported_count += 1
                print(f"✅ Imported: {title}")
                return True
            else:
                self.failed_count += 1
                error_msg = f"Failed to import '{title}': {result.get('message', 'Unknown error')}"
                self.errors.append(error_msg)
                print(f"❌ {error_msg}")
                return False
                
        except Exception as e:
            self.failed_count += 1
            error_msg = f"Exception importing conversation: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    async def import_claude_export(self, json_file: Path) -> None:
        """Import from Claude conversation export JSON"""
        try:
            print(f"📂 Reading {json_file}...")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📊 File loaded successfully")
            
            # Handle different JSON structures
            conversations = []
            
            if isinstance(data, list):
                conversations = data
                print(f"📋 Found {len(conversations)} conversations in array format")
            elif isinstance(data, dict):
                if 'conversations' in data:
                    conversations = data['conversations']
                    print(f"📋 Found {len(conversations)} conversations in 'conversations' key")
                elif 'chats' in data:
                    conversations = data['chats']
                    print(f"📋 Found {len(conversations)} conversations in 'chats' key")
                elif 'data' in data:
                    conversations = data['data']
                    print(f"📋 Found {len(conversations)} conversations in 'data' key")
                else:
                    # Treat the whole object as a single conversation
                    conversations = [data]
                    print(f"📋 Treating entire object as single conversation")
            
            if not conversations:
                print("❌ No conversations found in the JSON file")
                return
            
            print(f"🚀 Starting import of {len(conversations)} conversations...")
            
            # Process conversations in batches for better progress feedback
            batch_size = 10
            total_conversations = len(conversations)
            
            for i in range(0, total_conversations, batch_size):
                batch = conversations[i:i + batch_size]
                batch_end = min(i + batch_size, total_conversations)
                
                print(f"\n📦 Processing batch {i//batch_size + 1} ({i+1}-{batch_end} of {total_conversations})")
                
                for j, conv in enumerate(batch):
                    current_index = i + j + 1
                    print(f"  📝 [{current_index}/{total_conversations}] Processing conversation...")
                    
                    try:
                        conversation_data = self.extract_conversation_content(conv)
                        
                        if not conversation_data:
                            self.skipped_count += 1
                            print(f"  ⏭️  Skipped: No valid content found")
                            continue
                        
                        success = await self.import_conversation(conversation_data)
                        
                        # Small delay to avoid overwhelming the system
                        if not self.dry_run:
                            await asyncio.sleep(0.1)
                            
                    except Exception as e:
                        self.failed_count += 1
                        error_msg = f"Error processing conversation {current_index}: {e}"
                        self.errors.append(error_msg)
                        print(f"  ❌ {error_msg}")
                
                # Progress update
                processed = min(batch_end, total_conversations)
                progress = (processed / total_conversations) * 100
                print(f"📊 Progress: {processed}/{total_conversations} ({progress:.1f}%)")
                
                # Brief pause between batches
                if not self.dry_run and batch_end < total_conversations:
                    await asyncio.sleep(0.5)
                    
        except Exception as e:
            print(f"❌ Error reading JSON file: {e}")
            self.errors.append(f"JSON file error: {e}")
    
    def print_summary(self):
        """Print detailed import summary"""
        print(f"\n" + "="*60)
        print(f"📊 IMPORT SUMMARY")
        print(f"="*60)
        
        if self.dry_run:
            print(f"🔍 DRY RUN RESULTS:")
            print(f"   ✅ Would import: {self.imported_count}")
            print(f"   ⏭️  Would skip: {self.skipped_count}")
            print(f"   ❌ Would fail: {self.failed_count}")
        else:
            print(f"✅ Successfully imported: {self.imported_count}")
            print(f"⏭️  Skipped (no content): {self.skipped_count}")
            print(f"❌ Failed imports: {self.failed_count}")
        
        total_processed = self.imported_count + self.skipped_count + self.failed_count
        if total_processed > 0:
            success_rate = (self.imported_count / total_processed) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
        
        if self.errors:
            print(f"\n⚠️  Errors encountered ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:5], 1):
                print(f"  {i}. {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more errors")
                print(f"  💡 Run with --verbose to see all errors")
        
        if not self.dry_run and self.imported_count > 0:
            print(f"\n🎉 Import completed! Your conversations are now searchable.")
            print(f"💡 Try: search_conversations(\"<topic>\") to find relevant discussions")

async def main():
    parser = argparse.ArgumentParser(
        description='Enhanced bulk import for Claude conversation exports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to preview import
  python bulk_import_enhanced.py /path/to/conversations.json --dry-run
  
  # Import conversations
  python bulk_import_enhanced.py /path/to/conversations.json
  
  # Import with custom title prefix
  python bulk_import_enhanced.py /path/to/conversations.json --title-prefix "Archive"
        """
    )
    
    parser.add_argument('json_file', help='Path to Claude conversation export JSON file')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview import without actually importing')
    parser.add_argument('--title-prefix', help='Prefix to add to all conversation titles')
    parser.add_argument('--verbose', action='store_true', 
                       help='Show detailed error messages')
    
    args = parser.parse_args()
    
    json_path = Path(args.json_file)
    
    if not json_path.exists():
        print(f"❌ File does not exist: {json_path}")
        return 1
    
    if not json_path.suffix.lower() == '.json':
        print(f"⚠️  Warning: File doesn't have .json extension: {json_path}")
    
    print(f"🚀 Claude Conversation Import Tool")
    print(f"📂 Source: {json_path}")
    print(f"🔍 Mode: {'DRY RUN' if args.dry_run else 'IMPORT'}")
    
    if args.dry_run:
        print(f"💡 This is a dry run - no data will be imported")
    
    print(f"\n" + "-"*60)
    
    importer = EnhancedBulkImporter(dry_run=args.dry_run)
    
    try:
        await importer.import_claude_export(json_path)
    except KeyboardInterrupt:
        print(f"\n⏹️  Import interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    importer.print_summary()
    
    if args.dry_run:
        print(f"\n💡 Run without --dry-run to perform the actual import")
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
