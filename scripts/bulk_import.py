#!/usr/bin/env python3

# Add src directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
"""
Bulk Conversation Import Script for Claude Memory System

Supports importing multiple conversations from various formats:
- Text files (.txt, .md)
- JSON exports
- Directory of conversation files
- CSV format with structured data
"""

import os
import json
import csv
import sys
from datetime import datetime
from pathlib import Path
import asyncio
import argparse

# Add the MCP server path to use ConversationMemoryServer
sys.path.append('/home/adam/Code/claude-memory-mcp')
from server_fastmcp import ConversationMemoryServer

class BulkImporter:
    def __init__(self):
        self.memory_server = ConversationMemoryServer()
        self.imported_count = 0
        self.failed_count = 0
        self.errors = []
    
    async def import_text_file(self, file_path: Path, title: str = None, date: str = None):
        """Import a single text file as a conversation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use filename as title if not provided
            if not title:
                title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
            
            # Use file modification time if no date provided
            if not date:
                mtime = file_path.stat().st_mtime
                date = datetime.fromtimestamp(mtime).isoformat()
            
            result = await self.memory_server.add_conversation(content, title, date)
            
            if result.get('status') == 'success':
                self.imported_count += 1
                print(f"✅ Imported: {title}")
            else:
                self.failed_count += 1
                error_msg = f"Failed to import {file_path}: {result.get('message', 'Unknown error')}"
                self.errors.append(error_msg)
                print(f"❌ {error_msg}")
                
        except Exception as e:
            self.failed_count += 1
            error_msg = f"Exception importing {file_path}: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    async def import_directory(self, directory: Path, file_pattern: str = "*.txt"):
        """Import all matching files from a directory"""
        files = list(directory.glob(file_pattern))
        if not files:
            print(f"No files matching '{file_pattern}' found in {directory}")
            return
        
        print(f"Found {len(files)} files to import...")
        for file_path in files:
            await self.import_text_file(file_path)
    
    async def import_json_export(self, json_file: Path):
        """Import from a JSON export file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            conversations = []
            if isinstance(data, list):
                conversations = data
            elif 'conversations' in data:
                conversations = data['conversations']
            elif 'messages' in data:
                conversations = data['messages']
            
            for i, conv in enumerate(conversations):
                try:
                    content = conv.get('content', conv.get('text', str(conv)))
                    title = conv.get('title', f"Imported Conversation {i+1}")
                    date = conv.get('date', conv.get('timestamp'))
                    
                    await self.import_text_file(None, title, date)
                    # Manually add content since we're not reading from file
                    result = await self.memory_server.add_conversation(content, title, date)
                    
                    if result.get('status') == 'success':
                        self.imported_count += 1
                        print(f"✅ Imported: {title}")
                    else:
                        self.failed_count += 1
                        print(f"❌ Failed: {title}")
                        
                except Exception as e:
                    self.failed_count += 1
                    print(f"❌ Error processing conversation {i+1}: {e}")
                    
        except Exception as e:
            print(f"❌ Error reading JSON file: {e}")
    
    async def import_csv(self, csv_file: Path):
        """Import from CSV file (columns: title, content, date)"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    content = row.get('content', '')
                    title = row.get('title', f"CSV Import {i+1}")
                    date = row.get('date', row.get('timestamp'))
                    
                    if content:
                        result = await self.memory_server.add_conversation(content, title, date)
                        if result.get('status') == 'success':
                            self.imported_count += 1
                            print(f"✅ Imported: {title}")
                        else:
                            self.failed_count += 1
                            print(f"❌ Failed: {title}")
                    
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
    
    def print_summary(self):
        """Print import summary"""
        print(f"\n📊 Import Summary:")
        print(f"✅ Successfully imported: {self.imported_count}")
        print(f"❌ Failed imports: {self.failed_count}")
        
        if self.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"  • {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")

async def main():
    parser = argparse.ArgumentParser(description='Bulk import conversations to Claude Memory System')
    parser.add_argument('path', help='Path to file or directory to import')
    parser.add_argument('--format', choices=['text', 'json', 'csv', 'auto'], 
                       default='auto', help='Input format')
    parser.add_argument('--pattern', default='*.txt', 
                       help='File pattern for directory import (default: *.txt)')
    parser.add_argument('--title', help='Title for single file import')
    parser.add_argument('--date', help='Date for single file import (ISO format)')
    
    args = parser.parse_args()
    
    importer = BulkImporter()
    path = Path(args.path)
    
    if not path.exists():
        print(f"❌ Path does not exist: {path}")
        return
    
    if path.is_file():
        # Single file import
        if args.format == 'auto':
            if path.suffix.lower() == '.json':
                await importer.import_json_export(path)
            elif path.suffix.lower() == '.csv':
                await importer.import_csv(path)
            else:
                await importer.import_text_file(path, args.title, args.date)
        elif args.format == 'json':
            await importer.import_json_export(path)
        elif args.format == 'csv':
            await importer.import_csv(path)
        else:
            await importer.import_text_file(path, args.title, args.date)
    
    elif path.is_dir():
        # Directory import
        await importer.import_directory(path, args.pattern)
    
    importer.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
