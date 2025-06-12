#!/usr/bin/env python3
"""
Claude Conversation Memory MCP Server (FastMCP Version)

This MCP server provides tools for managing and searching Claude conversation history.
Supports storing conversations locally and retrieving context for current sessions.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Dict, List, Optional, Any, Union
from mcp.server.fastmcp import FastMCP

try:
    from .validators import (
        validate_title,
        validate_content,
        validate_date,
        validate_search_query,
        validate_limit
    )
    from .exceptions import ValidationError
    from .logging_config import (
        get_logger,
        log_function_call,
        log_performance,
        log_security_event,
        log_validation_failure,
        log_file_operation,
        init_default_logging
    )
except ImportError:
    # For direct imports during testing
    from validators import (
        validate_title,
        validate_content,
        validate_date,
        validate_search_query,
        validate_limit
    )
    from exceptions import ValidationError
    from logging_config import (
        get_logger,
        log_function_call,
        log_performance,
        log_security_event,
        log_validation_failure,
        log_file_operation,
        init_default_logging
    )

# Constants
DEFAULT_PREVIEW_LENGTH = 500
DEFAULT_CONTENT_PREVIEW = 200
MAX_PREVIEW_LINES = 10
CONTEXT_LINES_BEFORE = 2
CONTEXT_LINES_AFTER = 3
DEFAULT_SEARCH_LIMIT = 5
MAX_RESULTS_DISPLAY = 10
UTC_OFFSET_REPLACEMENT = '+00:00'

COMMON_TECH_TERMS = [
    'python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes',
    'terraform', 'mcp', 'api', 'database', 'sql', 'mongodb', 'redis',
    'git', 'github', 'vscode', 'linux', 'ubuntu', 'windows', 'wsl',
    'authentication', 'security', 'testing', 'deployment', 'ci/cd'
]


class ConversationMemoryServer:
    def __init__(self, storage_path: str = "~/claude-memory", use_data_dir: bool = None):
        # Initialize logging first
        init_default_logging()
        self.logger = get_logger("claude_memory_mcp.server")
        
        log_function_call("ConversationMemoryServer.__init__", storage_path=storage_path, use_data_dir=use_data_dir)
        
        self.storage_path = Path(storage_path).expanduser().resolve()
        
        try:
            self._validate_storage_path()
            
            # Auto-detect directory structure if not specified
            if use_data_dir is None:
                use_data_dir = self._detect_data_directory_structure()
            
            # Configure paths based on structure
            if use_data_dir:
                # New consolidated structure: data/conversations, data/summaries
                self.conversations_path = self.storage_path / "data" / "conversations"
                self.summaries_path = self.storage_path / "data" / "summaries"
                self.logger.info(f"Using new consolidated data/ directory structure")
            else:
                # Legacy structure: conversations/, summaries/ in storage root
                self.conversations_path = self.storage_path / "conversations"
                self.summaries_path = self.storage_path / "summaries"
                self.logger.info(f"Using legacy directory structure")
            
            self.index_file = self.conversations_path / "index.json"
            self.topics_file = self.conversations_path / "topics.json"
            
            # Ensure directories exist
            self.conversations_path.mkdir(parents=True, exist_ok=True)
            self.summaries_path.mkdir(parents=True, exist_ok=True)
            (self.summaries_path / "weekly").mkdir(exist_ok=True)
            
            self.logger.info(f"Server initialized successfully with storage: {self.storage_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize server: {str(e)}")
            raise
        
        # Initialize index files if they don't exist
        self._init_index_files()
    
    def _validate_storage_path(self):
        """Validate storage path for security"""
        log_function_call("_validate_storage_path", storage_path=str(self.storage_path))
        
        # Ensure path doesn't contain traversal attempts
        if '..' in str(self.storage_path):
            log_security_event("PATH_TRAVERSAL_ATTEMPT", f"Storage path contains '..' traversal: {self.storage_path}", "ERROR")
            raise ValueError("Storage path cannot contain '..' for security reasons")
        
        # Ensure path is within user's home directory or explicit allowed paths
        home = Path.home().resolve()
        if not str(self.storage_path).startswith(str(home)):
            log_security_event("PATH_OUTSIDE_HOME", f"Storage path outside home directory: {self.storage_path}", "ERROR")
            raise ValueError("Storage path must be within user's home directory")
        
        self.logger.debug(f"Storage path validation passed: {self.storage_path}")
    
    def _detect_data_directory_structure(self) -> bool:
        """
        Auto-detect whether to use new data/ structure or legacy structure.
        
        Returns:
            True if data/ directory exists and contains conversations/
            False for legacy structure (conversations/ in storage root)
        """
        data_conversations = self.storage_path / "data" / "conversations"
        legacy_conversations = self.storage_path / "conversations"
        
        # If data/conversations exists, use new structure
        if data_conversations.exists():
            self.logger.debug("Detected new data/ directory structure")
            return True
        
        # If conversations exists in root, use legacy structure  
        if legacy_conversations.exists():
            self.logger.debug("Detected legacy directory structure")
            return False
        
        # If neither exists, default to new structure for new installations
        self.logger.debug("No existing structure found, defaulting to new data/ structure")
        return True
    
    def _validate_file_path(self, file_path: Path) -> bool:
        """Validate that file path is within allowed storage directory"""
        try:
            file_path.resolve().relative_to(self.storage_path.resolve())
            self.logger.debug(f"File path validation passed: {file_path}")
            return True
        except ValueError:
            log_security_event("PATH_OUTSIDE_STORAGE", f"File path outside storage directory: {file_path}", "WARNING")
            self.logger.warning(f"File path validation failed: {file_path}")
            return False
    
    def _init_index_files(self):
        """Initialize index and topics files if they don't exist"""
        log_function_call("_init_index_files", index_exists=self.index_file.exists(), topics_exists=self.topics_file.exists())
        
        if not self.index_file.exists():
            with open(self.index_file, 'w') as f:
                json.dump({"conversations": [], "last_updated": datetime.now().isoformat()}, f)
            log_file_operation("create", str(self.index_file), True, file_type="index")
            self.logger.info(f"Created index file: {self.index_file}")
        
        if not self.topics_file.exists():
            with open(self.topics_file, 'w') as f:
                json.dump({"topics": {}, "last_updated": datetime.now().isoformat()}, f)
            log_file_operation("create", str(self.topics_file), True, file_type="topics")
            self.logger.info(f"Created topics file: {self.topics_file}")
    
    def _get_date_folder(self, date: datetime) -> Path:
        """Get the folder path for a given date"""
        year_folder = self.conversations_path / str(date.year)
        month_folder = year_folder / f"{date.month:02d}-{date.strftime('%B').lower()}"
        
        # Log if we're creating new directories
        creating_dirs = not month_folder.exists()
        month_folder.mkdir(parents=True, exist_ok=True)
        
        if creating_dirs:
            log_file_operation("create_directory", str(month_folder), True, date=date.strftime('%Y-%m'))
            self.logger.debug(f"Created date folder: {month_folder}")
        
        return month_folder
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from conversation content using simple keyword extraction"""
        start_time = time.time()
        topics = []
        content_lower = content.lower()
        
        tech_terms_found = 0
        for term in COMMON_TECH_TERMS:
            if term in content_lower:
                topics.append(term)
                tech_terms_found += 1
        
        # Extract quoted terms as potential topics
        quoted_terms = re.findall(r'"([^"]*)"', content)
        quoted_topics = [term.lower() for term in quoted_terms if len(term) > 2]
        topics.extend(quoted_topics)
        
        unique_topics = list(set(topics))  # Remove duplicates
        
        # Log topic extraction metrics
        duration = time.time() - start_time
        log_performance("_extract_topics", duration,
                       content_size=len(content),
                       tech_terms_found=tech_terms_found,
                       quoted_terms_found=len(quoted_topics),
                       total_topics=len(unique_topics))
        
        self.logger.debug(f"Extracted {len(unique_topics)} topics from {len(content)} chars")
        return unique_topics
    
    def _calculate_conversation_score(self, conv_info: dict, query_terms: List[str], file_path: Path) -> int:
        """Calculate relevance score for a conversation"""
        score = 0
        topics_matched = 0
        content_matches = 0
        
        # Check topics match
        for term in query_terms:
            if term in conv_info.get("topics", []):
                score += 3
                topics_matched += 1
        
        # Check content match
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                for term in query_terms:
                    term_count = content.count(term)
                    score += term_count
                    content_matches += term_count
        except (OSError, ValueError) as e:
            log_file_operation("read", str(file_path), False, error=str(e))
            self.logger.warning(f"Failed to read conversation file for scoring: {file_path}")
            return 0
        
        self.logger.debug(f"Conversation scored: {score} (topics: {topics_matched}, content: {content_matches})")
        return score

    async def search_conversations(self, query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> List[Dict[str, Any]]:
        """Search conversations for relevant content"""
        start_time = time.time()
        log_function_call("search_conversations", query=query[:50], limit=limit)
        
        try:
            # Validate inputs
            query = validate_search_query(query)
            limit = validate_limit(limit)
            
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
            final_results = results[:limit]
            
            # Log performance and results
            duration = time.time() - start_time
            log_performance("search_conversations", duration, 
                          results_found=len(final_results), 
                          total_conversations=len(index_data.get("conversations", [])),
                          query_length=len(query))
            
            self.logger.info(f"Search completed: '{query[:50]}' -> {len(final_results)} results")
            return final_results
            
        except ValidationError as e:
            log_validation_failure("search_query", query, str(e))
            self.logger.warning(f"Search validation failed: {str(e)}")
            return [{"error": f"Validation error: {str(e)}"}]
        except Exception as e:
            self.logger.error(f"Search failed for query '{query[:50]}': {str(e)}")
            return [{"error": f"Search failed: {str(e)}"}]
    
    def _get_preview(self, file_path: Path, query_terms: List[str]) -> str:
        """Get a preview of the conversation around the search terms"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            preview_lines = []
            match_found = False
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(term in line_lower for term in query_terms):
                    # Include context lines around the match
                    start = max(0, i - CONTEXT_LINES_BEFORE)
                    end = min(len(lines), i + CONTEXT_LINES_AFTER)
                    context = lines[start:end]
                    preview_lines.extend(context)
                    match_found = True
                    break
            
            preview = '\n'.join(preview_lines[:MAX_PREVIEW_LINES])
            final_preview = preview[:DEFAULT_PREVIEW_LENGTH] + "..." if len(preview) > DEFAULT_PREVIEW_LENGTH else preview
            
            self.logger.debug(f"Generated preview for {file_path}: {len(final_preview)} chars, match_found={match_found}")
            return final_preview
            
        except (OSError, ValueError) as e:
            log_file_operation("read", str(file_path), False, error=str(e))
            self.logger.warning(f"Failed to generate preview for {file_path}: {str(e)}")
            return "Preview unavailable"
    
    async def add_conversation(self, content: str, title: str = None, date: str = None) -> Dict[str, str]:
        """Add a new conversation to the memory system"""
        start_time = time.time()
        log_function_call("add_conversation", title=title, 
                         content_length=len(content) if content else 0, date=date)
        
        try:
            # Validate inputs
            content = validate_content(content)
            title = validate_title(title)
            conv_date = validate_date(date)
            
            # Use current date if not provided
            if not conv_date:
                conv_date = datetime.now()
            
            # Generate filename from sanitized title
            title_slug = re.sub(r'[^\w\s-]', '', title).strip()
            title_slug = re.sub(r'[-\s]+', '-', title_slug).lower()
            filename = f"{conv_date.strftime('%Y-%m-%d')}_{title_slug}.md"
            
            # Get date folder and create file
            date_folder = self._get_date_folder(conv_date)
            file_path = date_folder / filename
            
            # Extract topics
            topics = self._extract_topics(content)
            
            # Create conversation file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"**Date:** {conv_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Topics:** {', '.join(topics)}\n\n")
                f.write("---\n\n")
                f.write(content)
            
            # Update index
            await self._update_index(file_path, conv_date, topics, title)
            
            # Log successful operation
            duration = time.time() - start_time
            log_performance("add_conversation", duration, 
                          content_size=len(content), 
                          topics_extracted=len(topics),
                          file_path=str(file_path))
            log_file_operation("create", str(file_path), True, 
                             size_bytes=len(content), topics=len(topics))
            
            self.logger.info(f"Conversation saved: '{title}' -> {filename} ({len(content)} chars)")
            
            return {
                "status": "success",
                "file_path": str(file_path),
                "topics": topics,
                "message": f"Conversation saved successfully to {filename}"
            }
            
        except ValidationError as e:
            log_validation_failure("conversation_input", title or "untitled", str(e))
            self.logger.warning(f"Conversation validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Validation error: {str(e)}"
            }
        except Exception as e:
            log_file_operation("create", title or "unknown", False, error=str(e))
            self.logger.error(f"Failed to save conversation '{title}': {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to save conversation: {str(e)}"
            }
    
    async def _update_index(self, file_path: Path, date: datetime, topics: List[str], title: str):
        """Update the conversation index"""
        log_function_call("_update_index", file_path=str(file_path), topics_count=len(topics), title=title)
        
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
            
            old_count = len(index_data["conversations"])
            index_data["conversations"].append(conv_entry)
            index_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            log_file_operation("update", str(self.index_file), True, 
                             conversations_before=old_count, 
                             conversations_after=len(index_data["conversations"]))
            
            # Update topics index
            await self._update_topics_index(topics)
            
            self.logger.info(f"Index updated: added conversation '{title}' ({len(topics)} topics)")
            
        except Exception as e:
            log_file_operation("update", str(self.index_file), False, error=str(e))
            self.logger.error(f"Failed to update index: {e}")
            raise
    
    async def _update_topics_index(self, topics: List[str]):
        """Update the topics index"""
        if not topics:
            return
            
        log_function_call("_update_topics_index", topics_count=len(topics), topics=topics[:5])
        
        try:
            with open(self.topics_file, 'r') as f:
                topics_data = json.load(f)
            
            new_topics = 0
            updated_topics = 0
            
            for topic in topics:
                if topic in topics_data["topics"]:
                    topics_data["topics"][topic] += 1
                    updated_topics += 1
                else:
                    topics_data["topics"][topic] = 1
                    new_topics += 1
            
            topics_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.topics_file, 'w') as f:
                json.dump(topics_data, f, indent=2)
            
            log_file_operation("update", str(self.topics_file), True, 
                             new_topics=new_topics, updated_topics=updated_topics)
            
            self.logger.debug(f"Topics index updated: {new_topics} new, {updated_topics} updated")
                
        except Exception as e:
            log_file_operation("update", str(self.topics_file), False, error=str(e))
            self.logger.error(f"Failed to update topics index: {e}")
            raise
    
    def _calculate_week_range(self, week_offset: int = 0) -> tuple:
        """Calculate the date range for a specific week"""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        # Get start of current week (Monday at midnight)
        start_of_current_week = now - timedelta(days=now.weekday())
        start_of_current_week = start_of_current_week.replace(hour=0, minute=0, second=0, microsecond=0)
        target_week_start = start_of_current_week - timedelta(weeks=week_offset)
        target_week_end = target_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return target_week_start, target_week_end
    
    def _filter_conversations_by_week(self, index_data: dict, target_week_start: datetime, target_week_end: datetime) -> List[dict]:
        """Filter conversations that fall within the specified week"""
        week_conversations = []
        for conv_info in index_data.get("conversations", []):
            conv_date = datetime.fromisoformat(conv_info["date"].replace('Z', UTC_OFFSET_REPLACEMENT))
            # Convert to timezone-naive for comparison
            conv_date_naive = conv_date.replace(tzinfo=None)
            target_start_naive = target_week_start.replace(tzinfo=None)
            target_end_naive = target_week_end.replace(tzinfo=None)
            if target_start_naive <= conv_date_naive <= target_end_naive:
                week_conversations.append(conv_info)
        return week_conversations
    
    def _count_topics(self, week_conversations: List[dict]) -> dict:
        """Count frequency of topics across conversations"""
        topics_count = {}
        for conv_info in week_conversations:
            for topic in conv_info.get("topics", []):
                topics_count[topic] = topics_count.get(topic, 0) + 1
        return topics_count

    def _categorize_conversation(self, conv_info: dict) -> tuple:
        """Categorize a single conversation into coding/decisions/learning"""
        file_path = self.storage_path / conv_info["file_path"]
        
        if not file_path.exists():
            self.logger.debug(f"Conversation file missing for categorization: {file_path}")
            return False, False, False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            is_coding = any(term in content for term in ['code', 'function', 'class', 'def ', 'import ', 'git', 'repository'])
            is_decision = any(term in content for term in ['decided', 'chosen', 'selected', 'recommendation', 'approach'])
            is_learning = any(term in content for term in ['learn', 'tutorial', 'how to', 'explain', 'understand'])
            
            self.logger.debug(f"Conversation categorized: {conv_info['title']} -> coding={is_coding}, decision={is_decision}, learning={is_learning}")
            return is_coding, is_decision, is_learning
            
        except (OSError, ValueError) as e:
            log_file_operation("read", str(file_path), False, error=str(e))
            self.logger.warning(f"Failed to categorize conversation {file_path}: {str(e)}")
            return False, False, False

    def _analyze_conversations(self, week_conversations: List[dict]) -> tuple:
        """Analyze conversations to extract topics and categorize content"""
        topics_count = self._count_topics(week_conversations)
        coding_tasks = []
        decisions_made = []
        learning_topics = []
        
        for conv_info in week_conversations:
            is_coding, is_decision, is_learning = self._categorize_conversation(conv_info)
            
            if is_coding:
                coding_tasks.append(conv_info["title"])
            if is_decision:
                decisions_made.append(conv_info["title"])
            if is_learning:
                learning_topics.append(conv_info["title"])
        
        return topics_count, coding_tasks, decisions_made, learning_topics
    
    def _format_summary_header(self, target_week_start: datetime, target_week_end: datetime, 
                              week_offset: int, week_conversations: List[dict]) -> str:
        """Format the weekly summary header"""
        week_desc = "Current Week" if week_offset == 0 else f"Week of {target_week_start.strftime('%B %d, %Y')}"
        summary = f"# Weekly Summary: {week_desc}\n\n"
        summary += f"**Period:** {target_week_start.strftime('%Y-%m-%d')} to {target_week_end.strftime('%Y-%m-%d')}\n"
        summary += f"**Conversations:** {len(week_conversations)}\n\n"
        return summary

    def _format_topics_section(self, topics_count: dict) -> str:
        """Format the topics section"""
        if not topics_count:
            return ""
        
        section = "## 🏷️ Most Discussed Topics\n\n"
        sorted_topics = sorted(topics_count.items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_topics[:MAX_RESULTS_DISPLAY]:
            section += f"• **{topic}** ({count} conversation{'s' if count > 1 else ''})\n"
        section += "\n"
        return section

    def _format_category_section(self, title: str, emoji: str, items: List[str]) -> str:
        """Format a category section (coding, decisions, learning)"""
        if not items:
            return ""
        
        section = f"## {emoji} {title}\n\n"
        for item in items[:MAX_RESULTS_DISPLAY]:
            section += f"• {item}\n"
        section += "\n"
        return section

    def _format_conversations_list(self, week_conversations: List[dict]) -> str:
        """Format the conversations list section"""
        section = "## 📝 All Conversations\n\n"
        sorted_convs = sorted(week_conversations, key=lambda x: x["date"], reverse=True)
        
        for conv in sorted_convs:
            date_str = datetime.fromisoformat(conv["date"].replace('Z', UTC_OFFSET_REPLACEMENT)).strftime('%m/%d %H:%M')
            topics_str = ', '.join(conv.get("topics", [])[:3])
            if len(conv.get("topics", [])) > 3:
                topics_str += "..."
            section += f"• **{date_str}** - {conv['title']}\n"
            if topics_str:
                section += f"  *Topics: {topics_str}*\n"
        
        return section

    def _format_weekly_summary(self, week_conversations: List[dict], target_week_start: datetime, 
                              target_week_end: datetime, week_offset: int, topics_count: dict,
                              coding_tasks: List[str], decisions_made: List[str], learning_topics: List[str]) -> str:
        """Format the weekly summary content"""
        summary = self._format_summary_header(target_week_start, target_week_end, week_offset, week_conversations)
        summary += self._format_topics_section(topics_count)
        summary += self._format_category_section("Coding & Development", "💻", coding_tasks)
        summary += self._format_category_section("Decisions & Recommendations", "🎯", decisions_made)
        summary += self._format_category_section("Learning & Exploration", "📚", learning_topics)
        summary += self._format_conversations_list(week_conversations)
        
        return summary
    
    async def generate_weekly_summary(self, week_offset: int = 0) -> str:
        """Generate a summary of conversations from a specific week"""
        start_time = time.time()
        log_function_call("generate_weekly_summary", week_offset=week_offset)
        
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
                result = f"No conversations found for {week_desc} ({target_week_start.strftime('%Y-%m-%d')} to {target_week_end.strftime('%Y-%m-%d')})"
                self.logger.info(f"Weekly summary: no conversations found for {week_desc}")
                return result
            
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
            
            log_file_operation("create", str(summary_path), True, 
                             conversations=len(week_conversations),
                             topics=len(topics_count),
                             summary_length=len(summary))
            
            summary += f"\n---\n*Summary saved to {summary_path}*"
            
            # Log performance metrics
            duration = time.time() - start_time
            log_performance("generate_weekly_summary", duration,
                          week_offset=week_offset,
                          conversations_analyzed=len(week_conversations),
                          topics_found=len(topics_count),
                          coding_tasks=len(coding_tasks),
                          decisions=len(decisions_made),
                          learning_topics=len(learning_topics))
            
            self.logger.info(f"Weekly summary generated: {len(week_conversations)} conversations, {len(summary)} chars")
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate weekly summary: {str(e)}")
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
