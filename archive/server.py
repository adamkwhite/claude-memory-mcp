#!/usr/bin/env python3
"""
Claude Conversation Memory MCP Server

This MCP server provides tools for managing and searching Claude conversation history.
Supports storing conversations locally and retrieving context for current sessions.
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Dict, List, Optional, Any
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio


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
        # This is a basic implementation - can be enhanced with more sophisticated NLP
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
    
    async def generate_weekly_summary(self, week_offset: int = 0) -> str:
        """Generate a summary of conversations from a specific week"""
        try:
            # Calculate date range for the target week
            now = datetime.now()
            start_of_current_week = now - timedelta(days=now.weekday())
            target_week_start = start_of_current_week - timedelta(weeks=week_offset)
            target_week_end = target_week_start + timedelta(days=6, hours=23, minutes=59)
            
            # Load conversations from index
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            # Filter conversations for the target week
            week_conversations = []
            for conv_info in index_data.get("conversations", []):
                conv_date = datetime.fromisoformat(conv_info["date"].replace('Z', '+00:00'))
                if target_week_start <= conv_date <= target_week_end:
                    week_conversations.append(conv_info)
            
            if not week_conversations:
                week_desc = "current week" if week_offset == 0 else f"{week_offset} week(s) ago"
                return f"No conversations found for {week_desc} ({target_week_start.strftime('%Y-%m-%d')} to {target_week_end.strftime('%Y-%m-%d')})"
            
            # Analyze conversations
            topics_count = {}
            coding_tasks = []
            decisions_made = []
            learning_topics = []
            
            for conv_info in week_conversations:
                # Count topics
                for topic in conv_info.get("topics", []):
                    topics_count[topic] = topics_count.get(topic, 0) + 1
                
                # Try to identify coding tasks and decisions by loading conversation content
                file_path = self.storage_path / conv_info["file_path"]
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                        
                        # Look for coding indicators
                        if any(term in content for term in ['code', 'function', 'class', 'def ', 'import ', 'git', 'repository']):
                            coding_tasks.append(conv_info["title"])
                        
                        # Look for decision indicators
                        if any(term in content for term in ['decided', 'chosen', 'selected', 'recommendation', 'approach']):
                            decisions_made.append(conv_info["title"])
                        
                        # Look for learning indicators
                        if any(term in content for term in ['learn', 'tutorial', 'how to', 'explain', 'understand']):
                            learning_topics.append(conv_info["title"])
                            
                    except:
                        continue
            
            # Generate summary
            week_desc = "Current Week" if week_offset == 0 else f"Week of {target_week_start.strftime('%B %d, %Y')}"
            summary = f"# Weekly Summary: {week_desc}\n\n"
            summary += f"**Period:** {target_week_start.strftime('%Y-%m-%d')} to {target_week_end.strftime('%Y-%m-%d')}\n"
            summary += f"**Conversations:** {len(week_conversations)}\n\n"
            
            # Top topics
            if topics_count:
                summary += "## 🏷️ Most Discussed Topics\n\n"
                sorted_topics = sorted(topics_count.items(), key=lambda x: x[1], reverse=True)
                for topic, count in sorted_topics[:10]:
                    summary += f"• **{topic}** ({count} conversation{'s' if count > 1 else ''})\n"
                summary += "\n"
            
            # Coding tasks
            if coding_tasks:
                summary += "## 💻 Coding & Development\n\n"
                for task in coding_tasks[:10]:
                    summary += f"• {task}\n"
                summary += "\n"
            
            # Decisions made
            if decisions_made:
                summary += "## 🎯 Decisions & Recommendations\n\n"
                for decision in decisions_made[:10]:
                    summary += f"• {decision}\n"
                summary += "\n"
            
            # Learning topics
            if learning_topics:
                summary += "## 📚 Learning & Exploration\n\n"
                for topic in learning_topics[:10]:
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
            
            # Save summary to file
            summary_filename = f"week-{target_week_start.strftime('%Y-%m-%d')}.md"
            summary_path = self.summaries_path / "weekly" / summary_filename
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            summary += f"\n---\n*Summary saved to {summary_path}*"
            
            return summary
            
        except Exception as e:
            return f"Failed to generate weekly summary: {str(e)}"


# Initialize the MCP server
app = Server("claude-memory")
memory_server = ConversationMemoryServer()

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="search_conversations",
            description="Search through stored Claude conversations for relevant content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to find relevant conversations"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="add_conversation",
            description="Add a new conversation to the memory system",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The conversation content in markdown format"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title for the conversation (optional)"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date of the conversation in ISO format (optional, defaults to now)"
                    }
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="generate_weekly_summary",
            description="Generate a summary of conversations from the past week",
            inputSchema={
                "type": "object",
                "properties": {
                    "week_offset": {
                        "type": "integer",
                        "description": "Number of weeks back to summarize (0 = current week, 1 = last week, etc.)",
                        "default": 0
                    }
                }
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    if name == "search_conversations":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 5)
        
        results = await memory_server.search_conversations(query, limit)
        
        if not results:
            return [types.TextContent(
                type="text",
                text=f"No conversations found matching '{query}'"
            )]
        
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
        
        return [types.TextContent(type="text", text=response)]
    
    elif name == "add_conversation":
        content = arguments.get("content", "")
        title = arguments.get("title")
        date = arguments.get("date")
        
        result = await memory_server.add_conversation(content, title, date)
        
        return [types.TextContent(
            type="text",
            text=f"Status: {result['status']}\n{result['message']}"
        )]
    
    elif name == "generate_weekly_summary":
        week_offset = arguments.get("week_offset", 0)
        summary = await memory_server.generate_weekly_summary(week_offset)
        
        return [types.TextContent(
            type="text",
            text=summary
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="claude-memory",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
