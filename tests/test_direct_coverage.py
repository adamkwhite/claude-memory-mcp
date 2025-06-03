#!/usr/bin/env python3
"""
Direct tests for ConversationMemoryServer to achieve 50% coverage
without requiring FastMCP imports
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Mock the FastMCP import to avoid dependency issues
class MockFastMCP:
    def __init__(self, name):
        self.name = name
        self.tools = []
    
    def tool(self):
        def decorator(func):
            self.tools.append(func)
            return func
        return decorator
    
    def run(self):
        pass

# Patch the import before importing the server
sys.modules['mcp.server.fastmcp'] = type(sys)('mcp.server.fastmcp')
sys.modules['mcp.server.fastmcp'].FastMCP = MockFastMCP

# Add the server path for imports
sys.path.append('/home/adam/Code/claude-memory-mcp')

# Now import with mocked dependencies
from server_fastmcp import ConversationMemoryServer


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory for testing"""
    temp_dir = tempfile.mkdtemp(prefix="claude_memory_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def server(temp_storage):
    """Create a server instance for testing"""
    return ConversationMemoryServer(temp_storage)


class TestConversationMemoryServerDirect:
    """Direct tests for ConversationMemoryServer core functionality"""

    @pytest.mark.asyncio
    async def test_server_initialization(self, server, temp_storage):
        """Test server initialization creates all required directories"""
        assert server.storage_path == Path(temp_storage).expanduser()
        assert server.conversations_path.exists()
        assert server.summaries_path.exists()
        assert (server.summaries_path / "weekly").exists()
        assert server.index_file.exists()
        assert server.topics_file.exists()

    def test_init_index_files(self, server):
        """Test index file initialization"""
        # Index files should already exist from initialization
        with open(server.index_file, 'r') as f:
            index_data = json.load(f)
        assert "conversations" in index_data
        assert "last_updated" in index_data
        
        with open(server.topics_file, 'r') as f:
            topics_data = json.load(f)
        assert "topics" in topics_data
        assert "last_updated" in topics_data

    def test_get_date_folder(self, server):
        """Test date folder creation"""
        test_date = datetime(2025, 3, 15, 10, 30, 45)
        folder = server._get_date_folder(test_date)
        
        assert folder.exists()
        assert "2025" in str(folder)
        assert "03-march" in str(folder)

    def test_extract_topics_basic(self, server):
        """Test basic topic extraction"""
        content = "Discussion about Python programming and MCP development"
        topics = server._extract_topics(content)
        
        assert "python" in topics
        assert "mcp" in topics

    def test_extract_topics_quoted_terms(self, server):
        """Test extraction of quoted terms"""
        content = 'We discussed "machine learning" and "data science" projects'
        topics = server._extract_topics(content)
        
        assert "machine learning" in topics
        assert "data science" in topics

    def test_extract_topics_edge_cases(self, server):
        """Test topic extraction edge cases"""
        # Empty content
        assert server._extract_topics("") == []
        
        # Special characters only
        assert server._extract_topics("!@#$%^&*()") == []
        
        # Short quoted terms (should be filtered)
        topics = server._extract_topics('"a" "bb" "valid term"')
        assert "a" not in topics
        assert "bb" not in topics
        assert "valid term" in topics

    @pytest.mark.asyncio
    async def test_add_conversation_basic(self, server):
        """Test basic conversation addition"""
        content = "Test conversation about Python MCP development"
        title = "Test Conversation"
        date = "2025-01-15T10:30:00"
        
        result = await server.add_conversation(content, title, date)
        
        assert result['status'] == 'success'
        assert 'file_path' in result
        assert 'topics' in result
        assert Path(result['file_path']).exists()
        
        # Check topics were extracted
        assert 'python' in result['topics']
        assert 'mcp' in result['topics']

    @pytest.mark.asyncio
    async def test_add_conversation_no_title(self, server):
        """Test conversation addition without title"""
        content = "Test conversation content"
        
        result = await server.add_conversation(content)
        
        assert result['status'] == 'success'
        assert Path(result['file_path']).exists()

    @pytest.mark.asyncio
    async def test_add_conversation_no_date(self, server):
        """Test conversation addition without date (uses current time)"""
        content = "Test conversation content"
        title = "Current Time Test"
        
        result = await server.add_conversation(content, title)
        
        assert result['status'] == 'success'
        assert Path(result['file_path']).exists()

    @pytest.mark.asyncio
    async def test_search_conversations_basic(self, server):
        """Test basic conversation search"""
        # Add test data
        await server.add_conversation(
            "Python programming discussion",
            "Python Talk",
            "2025-01-15T10:30:00"
        )
        
        await server.add_conversation(
            "JavaScript development tips",
            "JS Tips",
            "2025-01-15T11:00:00"
        )
        
        # Search for Python
        results = await server.search_conversations("Python", limit=5)
        
        assert len(results) > 0
        python_found = any("Python" in r.get('title', '') for r in results)
        assert python_found

    @pytest.mark.asyncio
    async def test_search_conversations_scoring(self, server):
        """Test search result scoring"""
        # Add conversation with multiple matches
        await server.add_conversation(
            "Python programming with python libraries and python tools",
            "High Score Python Discussion",
            "2025-01-15T10:30:00"
        )
        
        await server.add_conversation(
            "General programming discussion",
            "Low Score Discussion",
            "2025-01-15T11:00:00"
        )
        
        results = await server.search_conversations("python", limit=2)
        
        assert len(results) > 0
        # First result should be the one with more matches
        assert results[0]['score'] > 0

    @pytest.mark.asyncio
    async def test_search_conversations_empty(self, server):
        """Test search with no results"""
        results = await server.search_conversations("nonexistentterm12345", limit=5)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_conversations_missing_file(self, server, temp_storage):
        """Test search when conversation file is missing"""
        # Add conversation
        result = await server.add_conversation(
            "Test content",
            "Test Title",
            "2025-01-15T10:30:00"
        )
        
        # Remove the file but keep index entry
        file_path = Path(result['file_path'])
        if file_path.exists():
            file_path.unlink()
        
        # Search should handle missing file gracefully
        results = await server.search_conversations("Test", limit=5)
        assert isinstance(results, list)  # Should not crash

    def test_get_preview_basic(self, server, temp_storage):
        """Test conversation preview generation"""
        # Create a test file
        test_file = Path(temp_storage) / "test_preview.md"
        content = """Line 1: Introduction
Line 2: This contains the search term
Line 3: Context after match
Line 4: More content"""
        
        with open(test_file, 'w') as f:
            f.write(content)
        
        preview = server._get_preview(test_file, ["search", "term"])
        assert len(preview) > 0
        assert "search term" in preview.lower()

    def test_get_preview_missing_file(self, server, temp_storage):
        """Test preview generation with missing file"""
        missing_file = Path(temp_storage) / "nonexistent.md"
        preview = server._get_preview(missing_file, ["search"])
        assert preview == "Preview unavailable"

    @pytest.mark.asyncio
    async def test_update_index(self, server, temp_storage):
        """Test index updating functionality"""
        test_date = datetime(2025, 1, 15, 10, 30)
        test_topics = ["python", "mcp"]
        test_title = "Index Test"
        
        # Create a fake file path
        fake_path = server.conversations_path / "2025" / "01-january" / "test.md"
        fake_path.parent.mkdir(parents=True, exist_ok=True)
        fake_path.touch()
        
        await server._update_index(fake_path, test_date, test_topics, test_title)
        
        # Check index was updated
        with open(server.index_file, 'r') as f:
            index_data = json.load(f)
        
        assert len(index_data['conversations']) > 0
        last_conv = index_data['conversations'][-1]
        assert last_conv['title'] == test_title
        assert last_conv['topics'] == test_topics

    @pytest.mark.asyncio
    async def test_update_topics_index(self, server):
        """Test topics index updating"""
        test_topics = ["python", "mcp", "python"]  # python appears twice
        
        await server._update_topics_index(test_topics)
        
        with open(server.topics_file, 'r') as f:
            topics_data = json.load(f)
        
        assert "python" in topics_data['topics']
        assert "mcp" in topics_data['topics']
        assert topics_data['topics']['python'] == 2  # Should count duplicates

    @pytest.mark.asyncio
    async def test_generate_weekly_summary_no_conversations(self, server):
        """Test weekly summary with no conversations"""
        summary = await server.generate_weekly_summary(0)
        assert "No conversations found" in summary
        assert "current week" in summary

    @pytest.mark.asyncio
    async def test_generate_weekly_summary_with_data(self, server):
        """Test weekly summary with conversation data"""
        # Add conversations for current week
        current_time = datetime.now()
        
        await server.add_conversation(
            "Python code development with git repository",
            "Coding Discussion",
            current_time.isoformat()
        )
        
        await server.add_conversation(
            "We decided to use the recommended approach",
            "Decision Made",
            current_time.isoformat()
        )
        
        await server.add_conversation(
            "Learning tutorial about new concepts",
            "Learning Session",
            current_time.isoformat()
        )
        
        summary = await server.generate_weekly_summary(0)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Weekly Summary" in summary
        assert "Coding Discussion" in summary
        assert "Decision Made" in summary
        assert "Learning Session" in summary

    @pytest.mark.asyncio
    async def test_generate_weekly_summary_past_week(self, server):
        """Test weekly summary for past week"""
        summary = await server.generate_weekly_summary(1)
        assert "No conversations found" in summary
        assert "1 week(s) ago" in summary

    @pytest.mark.asyncio
    async def test_generate_weekly_summary_error(self, server, temp_storage):
        """Test weekly summary error handling"""
        # Remove index file to cause error
        if server.index_file.exists():
            server.index_file.unlink()
        
        summary = await server.generate_weekly_summary(0)
        assert "Failed to generate weekly summary" in summary

    @pytest.mark.asyncio
    async def test_add_conversation_error_handling(self, server):
        """Test add conversation error handling"""
        # Test with invalid date
        result = await server.add_conversation(
            "Test content",
            "Error Test",
            "invalid-date-format"
        )
        
        # Should handle gracefully
        assert 'status' in result


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--cov=server_fastmcp", "--cov-report=html", "--cov-report=term"])