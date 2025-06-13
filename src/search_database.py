#!/usr/bin/env python3
"""
SQLite FTS-based search database for conversation memory.

This module provides optimized search functionality using SQLite's FTS5
extension for full-text search, replacing the linear search approach.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging


class SearchDatabase:
    """SQLite FTS5-based search database for conversations."""
    
    def __init__(self, db_path: str):
        """Initialize the search database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with FTS5 tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Create main conversations table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        date TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        topics_json TEXT,
                        topics_text TEXT
                    )
                """)
                
                # Create FTS5 virtual table for full-text search
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts USING fts5(
                        id,
                        title,
                        content,
                        topics_text,
                        content='conversations',
                        content_rowid='rowid'
                    )
                """)
                
                # Create topics table for topic-based searches
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_topics (
                        conversation_id TEXT,
                        topic TEXT,
                        FOREIGN KEY (conversation_id) REFERENCES conversations(id),
                        PRIMARY KEY (conversation_id, topic)
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_date ON conversations(date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_topics_topic ON conversation_topics(topic)")
                
                # Create triggers to maintain FTS5 table
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS conversations_ai AFTER INSERT ON conversations BEGIN
                        INSERT INTO conversations_fts(id, title, content, topics_text)
                        VALUES (new.id, new.title, new.content, new.topics_text);
                    END
                """)
                
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS conversations_ad AFTER DELETE ON conversations BEGIN
                        DELETE FROM conversations_fts WHERE id = old.id;
                    END
                """)
                
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS conversations_au AFTER UPDATE ON conversations BEGIN
                        UPDATE conversations_fts SET 
                            title = new.title,
                            content = new.content,
                            topics_text = new.topics_text
                        WHERE id = new.id;
                    END
                """)
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def add_conversation(self, conversation_data: Dict[str, Any], file_path: str) -> bool:
        """Add a conversation to the search database."""
        try:
            topics_json = json.dumps(conversation_data.get("topics", []))
            topics_text = " ".join(conversation_data.get("topics", []))
            
            with sqlite3.connect(self.db_path) as conn:
                # Insert into main table
                conn.execute("""
                    INSERT OR REPLACE INTO conversations 
                    (id, title, content, date, created_at, file_path, topics_json, topics_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation_data["id"],
                    conversation_data["title"],
                    conversation_data["content"],
                    conversation_data["date"],
                    conversation_data["created_at"],
                    file_path,
                    topics_json,
                    topics_text
                ))
                
                # Insert topics
                conn.execute("DELETE FROM conversation_topics WHERE conversation_id = ?", 
                           (conversation_data["id"],))
                
                for topic in conversation_data.get("topics", []):
                    conn.execute("""
                        INSERT INTO conversation_topics (conversation_id, topic)
                        VALUES (?, ?)
                    """, (conversation_data["id"], topic))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to add conversation {conversation_data.get('id', 'unknown')}: {e}")
            return False
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations using FTS5."""
        try:
            # Sanitize query for FTS5
            query_cleaned = self._sanitize_fts_query(query)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Use FTS5 MATCH for full-text search
                cursor = conn.execute("""
                    SELECT c.id, c.title, c.date, c.topics_json, c.file_path,
                           bm25(conversations_fts) as score,
                           snippet(conversations_fts, 2, '<mark>', '</mark>', '...', 32) as preview
                    FROM conversations_fts
                    JOIN conversations c ON conversations_fts.id = c.id
                    WHERE conversations_fts MATCH ?
                    ORDER BY bm25(conversations_fts)
                    LIMIT ?
                """, (query_cleaned, limit))
                
                results = []
                for row in cursor:
                    result = {
                        "id": row["id"],
                        "title": row["title"],
                        "date": row["date"],
                        "topics": json.loads(row["topics_json"]) if row["topics_json"] else [],
                        "score": float(row["score"]),
                        "preview": row["preview"],
                        "file_path": row["file_path"]
                    }
                    results.append(result)
                
                return results
                
        except sqlite3.Error as e:
            self.logger.error(f"Search failed: {e}")
            return [{"error": f"Search failed: {str(e)}"}]
    
    def search_by_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations by specific topic."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT c.id, c.title, c.date, c.topics_json, c.file_path
                    FROM conversations c
                    JOIN conversation_topics ct ON c.id = ct.conversation_id
                    WHERE ct.topic = ?
                    ORDER BY c.date DESC
                    LIMIT ?
                """, (topic, limit))
                
                results = []
                for row in cursor:
                    result = {
                        "id": row["id"],
                        "title": row["title"],
                        "date": row["date"],
                        "topics": json.loads(row["topics_json"]) if row["topics_json"] else [],
                        "file_path": row["file_path"]
                    }
                    results.append(result)
                
                return results
                
        except sqlite3.Error as e:
            self.logger.error(f"Topic search failed: {e}")
            return []
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(DISTINCT topic) FROM conversation_topics")
                unique_topics = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT topic, COUNT(*) as count 
                    FROM conversation_topics 
                    GROUP BY topic 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                popular_topics = [{"topic": row[0], "count": row[1]} for row in cursor]
                
                return {
                    "total_conversations": total_conversations,
                    "unique_topics": unique_topics,
                    "popular_topics": popular_topics
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Stats query failed: {e}")
            return {"error": str(e)}
    
    def _sanitize_fts_query(self, query: str) -> str:
        """Sanitize query string for FTS5 to prevent syntax errors."""
        # Remove special FTS5 characters that could cause syntax errors
        special_chars = ['"', "'", '(', ')', '[', ']', '{', '}', '*', ':', '-']
        sanitized = query
        
        for char in special_chars:
            sanitized = sanitized.replace(char, ' ')
        
        # Split into terms and rejoin
        terms = sanitized.split()
        
        # Filter out empty terms and very short terms
        terms = [term for term in terms if len(term) >= 2]
        
        if not terms:
            return "NOT_FOUND_EMPTY_QUERY"
        
        # Join with OR operator for broader search
        return ' OR '.join(terms)
    
    def rebuild_fts_index(self):
        """Rebuild the FTS5 index (useful after bulk imports)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO conversations_fts(conversations_fts) VALUES('rebuild')")
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"FTS index rebuild failed: {e}")
            raise
    
    def get_conversation_count(self) -> int:
        """Get total conversation count."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM conversations")
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            self.logger.error(f"Count query failed: {e}")
            return 0