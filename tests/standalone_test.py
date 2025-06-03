#!/usr/bin/env python3
"""
Standalone Test for Claude Conversation Memory System
Tests core functionality without MCP dependencies
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Dict, List, Optional, Any


class ConversationMemoryServer:
    def __init__(self, storage_path: str = "~/claude-memory"):
        self.storage_path = Path(storage_path).expanduser()
        self.conversations_path = self.storage_path / "conversations"
        self.summaries_path = self.storage_path / "summaries"
        self.index_file = self.conversations_path / "index.json"
        self.topics_file = self.conversations_path / "topics.json"
        
        # Ensure directories exist
        self.conversations_path.mkdir(parents=True, exist_ok=True)
        self.summaries_path.mkdir(parents=True, exist_ok=True)
        (self.summaries_path / "weekly").mkdir(exist_ok=True)
        
        # Initialize index files if they don't exist
        self._init_index_files()
    
    def _init_index_files(self):
        """Initialize index and topics files if they don't exist"""
        if not self.index_file.exists():
            with open(self.index_file, 'w') as f:
                json.dump({"conversations": [], "last_updated": datetime.now().isoformat()}, f)
        
        if not self.topics_file.exists():
            with open(self.topics_file, 'w') as f:
                json.dump({"topics": {}, "last_updated": datetime.now().isoformat()}, f)
    
    def _get_date_folder(self, date: datetime) -> Path:
        """Get the folder path for a given date"""
        year_folder = self.conversations_path / str(date.year)
        month_folder = year_folder / f"{date.month:02d}-{date.strftime('%B').lower()}"
        month_folder.mkdir(parents=True, exist_ok=True)
        return month_folder
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from conversation content using simple keyword extraction"""
        common_tech_terms = [
            'python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes',
            'terraform', 'mcp', 'api', 'database', 'sql', 'mongodb', 'redis',
            'git', 'github', 'vscode', 'linux', 'ubuntu', 'windows', 'wsl',
            'authentication', 'security', 'testing', 'deployment', 'ci/cd'
        ]
        
        topics = []
        content_lower = content.lower()
        
        for term in common_tech_terms:
            if term in content_lower:
                topics.append(term)
        
        # Extract quoted terms as potential topics
        quoted_terms = re.findall(r'"([^"]*)"', content)
        topics.extend([term.lower() for term in quoted_terms if len(term) > 2])
        
        return list(set(topics))  # Remove duplicates
    
    async def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search conversations for relevant content"""
        try:
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            results = []
            query_terms = query.lower().split()
            
            for conv_info in index_data.get("conversations", []):
                score = 0
                file_path = self.storage_path / conv_info["file_path"]
                
                if not file_path.exists():
                    continue
                
                # Check topics match
                for term in query_terms:
                    if term in conv_info.get("topics", []):
                        score += 3
                
                # Check content match
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for term in query_terms:
                            score += content.count(term)
                except:
                    continue
                
                if score > 0:
                    results.append({
                        "file_path": str(file_path),
                        "date": conv_info["date"],
                        "topics": conv_info.get("topics", []),
                        "title": conv_info.get("title", "Untitled Conversation"),
                        "score": score,
                        "preview": self._get_preview(file_path, query_terms)
                    })
            
            # Sort by score and return top results
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
    
    def _get_preview(self, file_path: Path, query_terms: List[str]) -> str:
        """Get a preview of the conversation around the search terms"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            preview_lines = []
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(term in line_lower for term in query_terms):
                    # Include context lines around the match
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context = lines[start:end]
                    preview_lines.extend(context)
                    break
            
            preview = '\n'.join(preview_lines[:10])  # Limit preview length
            return preview[:500] + "..." if len(preview) > 500 else preview
            
        except:
            return "Preview unavailable"
    
    async def add_conversation(self, content: str, title: str = None, date: str = None) -> Dict[str, str]:
        """Add a new conversation to the memory system"""
        try:
            # Parse date or use current date
            if date:
                conv_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            else:
                conv_date = datetime.now()
            
            # Generate filename
            title_slug = re.sub(r'[^\w\s-]', '', title or "conversation").strip()
            title_slug = re.sub(r'[-\s]+', '-', title_slug).lower()
            filename = f"{conv_date.strftime('%Y-%m-%d')}_{title_slug}.md"
            
            # Get date folder and create file
            date_folder = self._get_date_folder(conv_date)
            file_path = date_folder / filename
            
            # Extract topics
            topics = self._extract_topics(content)
            
            # Create conversation file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title or 'Claude Conversation'}\n\n")
                f.write(f"**Date:** {conv_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Topics:** {', '.join(topics)}\n\n")
                f.write("---\n\n")
                f.write(content)
            
            # Update index
            await self._update_index(file_path, conv_date, topics, title)
            
            return {
                "status": "success",
                "file_path": str(file_path),
                "topics": topics,
                "message": f"Conversation saved successfully to {filename}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to save conversation: {str(e)}"
            }
    
    async def _update_index(self, file_path: Path, date: datetime, topics: List[str], title: str):
        """Update the conversation index"""
        try:
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            # Add conversation to index
            relative_path = file_path.relative_to(self.storage_path)
            conv_entry = {
                "file_path": str(relative_path),
                "date": date.isoformat(),
                "topics": topics,
                "title": title or "Untitled Conversation",
                "added": datetime.now().isoformat()
            }
            
            index_data["conversations"].append(conv_entry)
            index_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            # Update topics index
            await self._update_topics_index(topics)
            
        except Exception as e:
            print(f"Failed to update index: {e}")
    
    async def _update_topics_index(self, topics: List[str]):
        """Update the topics index"""
        try:
            with open(self.topics_file, 'r') as f:
                topics_data = json.load(f)
            
            for topic in topics:
                if topic in topics_data["topics"]:
                    topics_data["topics"][topic] += 1
                else:
                    topics_data["topics"][topic] = 1
            
            topics_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.topics_file, 'w') as f:
                json.dump(topics_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to update topics index: {e}")


async def test_conversation_memory():
    """Test the conversation memory system"""
    print("🧪 Testing Claude Conversation Memory System...")
    
    # Initialize server with test directory
    test_path = "/home/adam/claude-memory-test"
    server = ConversationMemoryServer(test_path)
    
    print(f"📁 Using test directory: {test_path}")
    
    # Test 1: Add a conversation
    print("\n1️⃣ Testing conversation addition...")
    test_content = """
# Test Conversation

**Human**: How do I set up a Python MCP server?

**Claude**: To set up a Python MCP server, you need to:
1. Install the mcp package
2. Create a server.py file with the MCP server code
3. Define your tools and handlers
4. Configure Claude Desktop to use your server

The key is to implement the proper MCP protocol.
"""
    
    result = await server.add_conversation(
        content=test_content,
        title="MCP Server Setup Discussion",
        date="2025-01-15T10:30:00"
    )
    
    print(f"✅ Add conversation result: {result['status']}")
    if result['status'] == 'success':
        print(f"   📄 File: {result['file_path']}")
        print(f"   🏷️  Topics: {result['topics']}")
    else:
        print(f"❌ Error: {result['message']}")
        return False
    
    # Test 2: Search conversations
    print("\n2️⃣ Testing conversation search...")
    search_results = await server.search_conversations("MCP server", limit=3)
    
    if search_results and not any("error" in result for result in search_results):
        print(f"✅ Found {len(search_results)} conversations")
        for i, result in enumerate(search_results, 1):
            print(f"   {i}. {result['title']} (score: {result['score']})")
    else:
        print(f"❌ Search failed or no results found")
        return False
    
    # Test 3: Verify file structure
    print("\n3️⃣ Testing file structure...")
    expected_files = [
        Path(test_path) / "conversations" / "index.json",
        Path(test_path) / "conversations" / "topics.json",
        Path(test_path) / "summaries" / "weekly"
    ]
    
    all_exist = True
    for file_path in expected_files:
        if file_path.exists():
            print(f"   ✅ {file_path.name}")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_exist = False
    
    print(f"\n🎉 Core functionality test {'PASSED' if all_exist else 'FAILED'}!")
    return all_exist


if __name__ == "__main__":
    asyncio.run(test_conversation_memory())
