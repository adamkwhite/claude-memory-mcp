#!/usr/bin/env python3
"""
Common ConversationMemoryServer implementation

This module contains the core conversation memory functionality
shared between the FastMCP server and standalone implementations.
"""

import json
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
            "python", "javascript", "java", "css", "html", "react", "vue", "angular",
            "django", "flask", "nodejs", "express", "api", "database", "sql", "mongodb",
            "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "gitlab",
            "testing", "debugging", "deployment", "authentication", "security", "encryption",
            "machine learning", "ai", "neural network", "data science", "analytics",
            "frontend", "backend", "fullstack", "devops", "cicd", "microservices",
            "rest", "graphql", "websocket", "json", "xml", "yaml", "markdown",
            "linux", "windows", "macos", "bash", "powershell", "terminal", "cli",
            "performance", "optimization", "scalability", "architecture", "design patterns",
            "agile", "scrum", "kanban", "project management", "code review"
        ]
        
        # Convert to lowercase for matching
        content_lower = content.lower()
        
        # Find quoted terms (likely important concepts)
        quoted_terms = re.findall(r'"([^"]+)"', content)
        quoted_terms.extend(re.findall(r"'([^']+)'", content))
        
        # Find technical terms
        found_topics = []
        for term in common_tech_terms:
            if term in content_lower:
                found_topics.append(term)
        
        # Add quoted terms (filtered for reasonable length)
        for term in quoted_terms:
            if len(term) > 2 and len(term) < 50 and term.lower() not in found_topics:
                found_topics.append(term.lower())
        
        # Find capitalized words that might be technologies/frameworks
        tech_pattern = r'\b[A-Z][a-zA-Z]*(?:[A-Z][a-zA-Z]*)*\b'
        capitalized_words = re.findall(tech_pattern, content)
        for word in capitalized_words:
            if len(word) > 2 and word.lower() not in found_topics and word not in ["The", "This", "That", "When", "Where", "How", "What", "Why"]:
                found_topics.append(word.lower())
        
        return found_topics[:10]  # Limit to top 10 topics
    
    def add_conversation(self, content: str, title: str = None, conversation_date: str = None) -> Dict[str, Any]:
        """Add a new conversation to storage"""
        try:
            # Parse date or use current
            if conversation_date:
                try:
                    date = datetime.fromisoformat(conversation_date.replace('Z', '+00:00'))
                except ValueError:
                    date = datetime.now()
            else:
                date = datetime.now()
            
            # Generate title if not provided
            if not title:
                # Extract first line or first 50 characters as title
                lines = content.strip().split('\n')
                first_line = lines[0] if lines else content
                title = first_line[:50] + "..." if len(first_line) > 50 else first_line
            
            # Create conversation record
            conversation_id = f"conv_{date.strftime('%Y%m%d_%H%M%S')}_{hash(content) % 10000:04d}"
            
            date_folder = self._get_date_folder(date)
            file_path = date_folder / f"{conversation_id}.json"
            
            # Extract topics
            topics = self._extract_topics(content)
            
            conversation_data = {
                "id": conversation_id,
                "title": title,
                "content": content,
                "date": date.isoformat(),
                "topics": topics,
                "created_at": datetime.now().isoformat()
            }
            
            # Save conversation file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            # Update index
            self._update_index(conversation_data, file_path)
            
            # Update topics index
            self._update_topics_index(topics, conversation_id)
            
            return {
                "status": "success",
                "file_path": str(file_path),
                "topics": topics,
                "message": f"Conversation saved successfully with ID: {conversation_id}"
            }
            
        except (IOError, OSError, ValueError, TypeError) as e:
            return {
                "status": "error",
                "message": f"Failed to save conversation: {str(e)}"
            }
    
    def _calculate_search_score(self, query_terms: List[str], content: str, title: str, topics: List[str]) -> int:
        """Calculate relevance score for a conversation based on query terms"""
        score = 0
        for term in query_terms:
            score += content.count(term) * 1
            score += title.count(term) * 3
            if term in topics:
                score += 5
        return score
    
    def _process_conversation_for_search(self, conv_info: dict, query_terms: List[str]) -> Optional[dict]:
        """Process a single conversation for search results"""
        try:
            file_path = self.storage_path / conv_info["file_path"]
            if not file_path.exists():
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
            
            content = conv_data.get("content", "").lower()
            title = conv_data.get("title", "").lower()
            topics = [t.lower() for t in conv_data.get("topics", [])]
            
            score = self._calculate_search_score(query_terms, content, title, topics)
            
            if score > 0:
                return {
                    "id": conv_data["id"],
                    "title": conv_data["title"],
                    "date": conv_data["date"],
                    "topics": conv_data["topics"],
                    "score": score,
                    "preview": content[:200] + "..." if len(content) > 200 else content
                }
            return None
            
        except (IOError, ValueError, KeyError, TypeError):
            return None

    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations by content and topics"""
        try:
            # Load index
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            conversations = index_data.get("conversations", [])
            query_terms = query.lower().split()
            
            results = []
            for conv_info in conversations:
                result = self._process_conversation_for_search(conv_info, query_terms)
                if result:
                    results.append(result)
            
            # Sort by score and return top results
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except (IOError, OSError, ValueError, KeyError, TypeError) as e:
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
            
        except (IOError, ValueError, KeyError, TypeError):
            return "Preview unavailable"
    
    def get_preview(self, conversation_id: str) -> str:
        """Get a preview of a specific conversation"""
        try:
            # Load index to find the conversation
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            conversations = index_data.get("conversations", [])
            
            for conv_info in conversations:
                if conv_info["id"] == conversation_id:
                    file_path = self.storage_path / conv_info["file_path"]
                    
                    if file_path.exists():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            conv_data = json.load(f)
                        
                        content = conv_data.get("content", "")
                        return content[:500] + "..." if len(content) > 500 else content
                    else:
                        return "Conversation file not found"
            
            return "Conversation not found"
            
        except (IOError, OSError, ValueError, KeyError, TypeError) as e:
            return f"Error retrieving conversation: {str(e)}"
    
    def _update_index(self, conversation_data: Dict, file_path: Path):
        """Update the main index with new conversation"""
        try:
            # Load existing index
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            # Add new conversation to index
            relative_path = file_path.relative_to(self.storage_path)
            conv_entry = {
                "id": conversation_data["id"],
                "title": conversation_data["title"],
                "date": conversation_data["date"],
                "topics": conversation_data["topics"],
                "file_path": str(relative_path),
                "added_at": datetime.now().isoformat()
            }
            
            index_data["conversations"].append(conv_entry)
            index_data["last_updated"] = datetime.now().isoformat()
            
            # Save updated index
            with open(self.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
                
        except (IOError, OSError, ValueError, KeyError, TypeError) as e:
            print(f"Error updating index: {e}")
    
    def _update_topics_index(self, topics: List[str], conversation_id: str):
        """Update the topics index with new conversation topics"""
        try:
            # Load existing topics index
            with open(self.topics_file, 'r') as f:
                topics_data = json.load(f)
            
            topics_index = topics_data.get("topics", {})
            
            # Add conversation to each topic
            for topic in topics:
                if topic not in topics_index:
                    topics_index[topic] = []
                
                topics_index[topic].append({
                    "conversation_id": conversation_id,
                    "added_at": datetime.now().isoformat()
                })
            
            topics_data["topics"] = topics_index
            topics_data["last_updated"] = datetime.now().isoformat()
            
            # Save updated topics index
            with open(self.topics_file, 'w') as f:
                json.dump(topics_data, f, indent=2)
                
        except (IOError, OSError, ValueError, KeyError, TypeError) as e:
            print(f"Error updating topics index: {e}")
    
    def generate_weekly_summary(self, week_offset: int = 0) -> str:
        """Generate a weekly summary of conversations"""
        try:
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday() + (week_offset * 7))
            end_of_week = start_of_week + timedelta(days=6)

            week_conversations = self._get_week_conversations(start_of_week, end_of_week)
            if not week_conversations:
                return f"No conversations found for week of {start_of_week.strftime('%Y-%m-%d')}"

            summary_text = self._build_weekly_summary_text(start_of_week, end_of_week, week_conversations)

            summary_filename = f"week-{start_of_week.strftime('%Y-%m-%d')}.md"
            summary_file = self.summaries_path / "weekly" / summary_filename
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_text)

            summary_text += f"\n---\n*Summary saved to {summary_file}*"
            return summary_text

        except (IOError, OSError, ValueError, KeyError, TypeError) as e:
            return f"Failed to generate weekly summary: {str(e)}"

    def _get_week_conversations(self, start_of_week: datetime, end_of_week: datetime) -> List[dict]:
        """Return conversations for the given week range"""
        try:
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            conversations = index_data.get("conversations", [])
        except (IOError, OSError, ValueError, KeyError, TypeError):
            return []

        week_conversations = []
        for conv_info in conversations:
            try:
                conv_date = datetime.fromisoformat(conv_info["date"].replace('Z', '+00:00'))
                if start_of_week.date() <= conv_date.date() <= end_of_week.date():
                    file_path = self.storage_path / conv_info["file_path"]
                    if file_path.exists():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                conv_data = json.load(f)
                            week_conversations.append(conv_data)
                        except (IOError, UnicodeDecodeError, ValueError, KeyError, TypeError):
                            week_conversations.append({
                                "title": conv_info.get("title", "Untitled"),
                                "date": conv_info["date"],
                                "topics": conv_info.get("topics", [])
                            })
            except (ValueError, KeyError, TypeError):
                continue
        return week_conversations

    def _build_weekly_summary_text(self, start_of_week: datetime, end_of_week: datetime, week_conversations: List[dict]) -> str:
        """Build the markdown summary text for the week"""
        summary_parts = []
        summary_parts.append(f"# Weekly Summary: {start_of_week.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}")
        summary_parts.append(f"\n## Overview\n- Total conversations: {len(week_conversations)}")

        all_topics = []
        for conv in week_conversations:
            all_topics.extend(conv.get("topics", []))

        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        if topic_counts:
            summary_parts.append("\n## Popular Topics")
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics[:10]:
                summary_parts.append(f"- {topic}: {count} conversations")

        summary_parts.append("\n## Conversations")
        for conv in week_conversations:
            date_str = conv.get("date", "").split("T")[0]
            topics_str = ', '.join(conv.get("topics", [])[:3])
            if len(conv.get("topics", [])) > 3:
                topics_str += "..."
            conv_line = f"- [{date_str}] {conv.get('title', 'Untitled')}"
            if topics_str:
                conv_line += f" *Topics: {topics_str}*"
            summary_parts.append(conv_line)

        return "\n".join(summary_parts)
