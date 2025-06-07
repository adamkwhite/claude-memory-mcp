#!/usr/bin/env python3
"""
Claude Conversation Memory MCP Server (FastMCP Version)

This MCP server provides tools for managing and searching Claude conversation history.
Supports storing conversations locally and retrieving context for current sessions.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Dict, List, Optional, Any, Union
from mcp.server.fastmcp import FastMCP

# Constants
DEFAULT_PREVIEW_LENGTH = 500
DEFAULT_CONTENT_PREVIEW = 200
MAX_PREVIEW_LINES = 10
CONTEXT_LINES_BEFORE = 2
CONTEXT_LINES_AFTER = 3
DEFAULT_SEARCH_LIMIT = 5
MAX_RESULTS_DISPLAY = 10

COMMON_TECH_TERMS = [
    'python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes',
    'terraform', 'mcp', 'api', 'database', 'sql', 'mongodb', 'redis',
    'git', 'github', 'vscode', 'linux', 'ubuntu', 'windows', 'wsl',
    'authentication', 'security', 'testing', 'deployment', 'ci/cd'
]


class ConversationMemoryServer:
    def __init__(self, storage_path: str = "~/claude-memory"):
        self.storage_path = Path(storage_path).expanduser().resolve()
        self._validate_storage_path()
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
    
    def _validate_storage_path(self):
        """Validate storage path for security"""
        # Ensure path doesn't contain traversal attempts
        if '..' in str(self.storage_path):
            raise ValueError("Storage path cannot contain '..' for security reasons")
        
        # Ensure path is within user's home directory or explicit allowed paths
        home = Path.home().resolve()
        if not str(self.storage_path).startswith(str(home)):
            raise ValueError("Storage path must be within user's home directory")
    
    def _validate_file_path(self, file_path: Path) -> bool:
        """Validate that file path is within allowed storage directory"""
        try:
            file_path.resolve().relative_to(self.storage_path.resolve())
            return True
        except ValueError:
            return False
    
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
        topics = []
        content_lower = content.lower()
        
        for term in COMMON_TECH_TERMS:
            if term in content_lower:
                topics.append(term)
        
        # Extract quoted terms as potential topics
        quoted_terms = re.findall(r'"([^"]*)"', content)
        topics.extend([term.lower() for term in quoted_terms if len(term) > 2])
        
        return list(set(topics))  # Remove duplicates
    
    def _calculate_conversation_score(self, conv_info: dict, query_terms: List[str], file_path: Path) -> int:
        """Calculate relevance score for a conversation"""
        score = 0
        
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
        except (OSError, ValueError):
            return 0
            
        return score

    async def search_conversations(self, query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> List[Dict[str, Any]]:
        """Search conversations for relevant content"""
        try:
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            results = []
            query_terms = query.lower().split()
            
            for conv_info in index_data.get("conversations", []):
                file_path = self.storage_path / conv_info["file_path"]
                
                if not file_path.exists() or not self._validate_file_path(file_path):
                    continue
                
                score = self._calculate_conversation_score(conv_info, query_terms, file_path)
                
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
                    start = max(0, i - CONTEXT_LINES_BEFORE)
                    end = min(len(lines), i + CONTEXT_LINES_AFTER)
                    context = lines[start:end]
                    preview_lines.extend(context)
                    break
            
            preview = '\n'.join(preview_lines[:MAX_PREVIEW_LINES])
            return preview[:DEFAULT_PREVIEW_LENGTH] + "..." if len(preview) > DEFAULT_PREVIEW_LENGTH else preview
            
        except (OSError, ValueError):
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
    
    def _calculate_week_range(self, week_offset: int = 0) -> tuple:
        """Calculate the date range for a specific week"""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        start_of_current_week = now - timedelta(days=now.weekday())
        target_week_start = start_of_current_week - timedelta(weeks=week_offset)
        target_week_end = target_week_start + timedelta(days=6, hours=23, minutes=59)
        return target_week_start, target_week_end
    
    def _filter_conversations_by_week(self, index_data: dict, target_week_start: datetime, target_week_end: datetime) -> List[dict]:
        """Filter conversations that fall within the specified week"""
        week_conversations = []
        for conv_info in index_data.get("conversations", []):
            conv_date = datetime.fromisoformat(conv_info["date"].replace('Z', '+00:00'))
            # Convert to timezone-naive for comparison
            conv_date_naive = conv_date.replace(tzinfo=None)
            target_start_naive = target_week_start.replace(tzinfo=None)
            target_end_naive = target_week_end.replace(tzinfo=None)
            if target_start_naive <= conv_date_naive <= target_end_naive:
                week_conversations.append(conv_info)
        return week_conversations
    
    def _analyze_conversations(self, week_conversations: List[dict]) -> tuple:
        """Analyze conversations to extract topics and categorize content"""
        topics_count = {}
        coding_tasks = []
        decisions_made = []
        learning_topics = []
        
        for conv_info in week_conversations:
            # Count topics
            for topic in conv_info.get("topics", []):
                topics_count[topic] = topics_count.get(topic, 0) + 1
            
            # Analyze conversation content
            file_path = self.storage_path / conv_info["file_path"]
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    # Categorize conversations
                    if any(term in content for term in ['code', 'function', 'class', 'def ', 'import ', 'git', 'repository']):
                        coding_tasks.append(conv_info["title"])
                    
                    if any(term in content for term in ['decided', 'chosen', 'selected', 'recommendation', 'approach']):
                        decisions_made.append(conv_info["title"])
                    
                    if any(term in content for term in ['learn', 'tutorial', 'how to', 'explain', 'understand']):
                        learning_topics.append(conv_info["title"])
                        
                except (OSError, ValueError):
                    continue
        
        return topics_count, coding_tasks, decisions_made, learning_topics
    
    def _format_weekly_summary(self, week_conversations: List[dict], target_week_start: datetime, 
                              target_week_end: datetime, week_offset: int, topics_count: dict,
                              coding_tasks: List[str], decisions_made: List[str], learning_topics: List[str]) -> str:
        """Format the weekly summary content"""
        week_desc = "Current Week" if week_offset == 0 else f"Week of {target_week_start.strftime('%B %d, %Y')}"
        summary = f"# Weekly Summary: {week_desc}\n\n"
        summary += f"**Period:** {target_week_start.strftime('%Y-%m-%d')} to {target_week_end.strftime('%Y-%m-%d')}\n"
        summary += f"**Conversations:** {len(week_conversations)}\n\n"
        
        # Top topics
        if topics_count:
            summary += "## 🏷️ Most Discussed Topics\n\n"
            sorted_topics = sorted(topics_count.items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics[:MAX_RESULTS_DISPLAY]:
                summary += f"• **{topic}** ({count} conversation{'s' if count > 1 else ''})\n"
            summary += "\n"
        
        # Coding tasks
        if coding_tasks:
            summary += "## 💻 Coding & Development\n\n"
            for task in coding_tasks[:MAX_RESULTS_DISPLAY]:
                summary += f"• {task}\n"
            summary += "\n"
        
        # Decisions made
        if decisions_made:
            summary += "## 🎯 Decisions & Recommendations\n\n"
            for decision in decisions_made[:MAX_RESULTS_DISPLAY]:
                summary += f"• {decision}\n"
            summary += "\n"
        
        # Learning topics
        if learning_topics:
            summary += "## 📚 Learning & Exploration\n\n"
            for topic in learning_topics[:MAX_RESULTS_DISPLAY]:
                summary += f"• {topic}\n"
            summary += "\n"
        
        # Conversation list
        summary += "## 📝 All Conversations\n\n"
        sorted_convs = sorted(week_conversations, key=lambda x: x["date"], reverse=True)
        for conv in sorted_convs:
            date_str = datetime.fromisoformat(conv["date"].replace('Z', '+00:00')).strftime('%m/%d %H:%M')
            topics_str = ', '.join(conv.get("topics", [])[:3])
            if len(conv.get("topics", [])) > 3:
                topics_str += "..."
            summary += f"• **{date_str}** - {conv['title']}\n"
            if topics_str:
                summary += f"  *Topics: {topics_str}*\n"
        
        return summary
    
    async def generate_weekly_summary(self, week_offset: int = 0) -> str:
        """Generate a summary of conversations from a specific week"""
        try:
            # Calculate date range
            target_week_start, target_week_end = self._calculate_week_range(week_offset)
            
            # Load conversations from index
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            # Filter conversations for the target week
            week_conversations = self._filter_conversations_by_week(index_data, target_week_start, target_week_end)
            
            if not week_conversations:
                week_desc = "current week" if week_offset == 0 else f"{week_offset} week(s) ago"
                return f"No conversations found for {week_desc} ({target_week_start.strftime('%Y-%m-%d')} to {target_week_end.strftime('%Y-%m-%d')})"
            
            # Analyze conversations
            topics_count, coding_tasks, decisions_made, learning_topics = self._analyze_conversations(week_conversations)
            
            # Format summary
            summary = self._format_weekly_summary(week_conversations, target_week_start, target_week_end, 
                                                week_offset, topics_count, coding_tasks, decisions_made, learning_topics)
            
            # Save summary to file
            summary_filename = f"week-{target_week_start.strftime('%Y-%m-%d')}.md"
            summary_path = self.summaries_path / "weekly" / summary_filename
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            summary += f"\n---\n*Summary saved to {summary_path}*"
            
            return summary
            
        except Exception as e:
            return f"Failed to generate weekly summary: {str(e)}"


# Initialize FastMCP server and memory system
mcp = FastMCP("claude-memory")
memory_server = ConversationMemoryServer()

@mcp.tool()
async def search_conversations(query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> str:
    """Search through stored Claude conversations for relevant content"""
    results = await memory_server.search_conversations(query, limit)
    
    if not results:
        return f"No conversations found matching '{query}'"
    
    response = f"Found {len(results)} conversations matching '{query}':\n\n"
    for i, result in enumerate(results, 1):
        if "error" in result:
            response += f"Error: {result['error']}\n"
            continue
            
        response += f"**{i}. {result['title']}**\n"
        response += f"Date: {result['date']}\n"
        response += f"Topics: {', '.join(result['topics'])}\n"
        response += f"Relevance Score: {result['score']}\n"
        response += f"Preview:\n```\n{result['preview']}\n```\n\n"
    
    return response

@mcp.tool()
async def add_conversation(content: str, title: Optional[str] = None, date: Optional[str] = None) -> str:
    """Add a new conversation to the memory system"""
    result = await memory_server.add_conversation(content, title, date)
    return f"Status: {result['status']}\n{result['message']}"

@mcp.tool()
async def generate_weekly_summary(week_offset: int = 0) -> str:
    """Generate a summary of conversations from the past week"""
    return await memory_server.generate_weekly_summary(week_offset)

if __name__ == "__main__":
    mcp.run()
