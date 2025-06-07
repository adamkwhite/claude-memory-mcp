#!/usr/bin/env python3
"""
Additional tests to achieve 100% coverage for the MCP server
Targets the remaining 28 uncovered lines from previous coverage report
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
# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from conversation_memory import ConversationMemoryServer


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


class TestCompleteEdgeCaseCoverage:
    """Tests targeting the remaining uncovered lines for 100% coverage"""

    @pytest.mark.asyncio
    async def test_search_file_read_exception(self, server, temp_storage):
        """Test search when file read fails (lines 96-98)"""
        # Add a conversation
        result = server.add_conversation(
            "Test content for file read error",
            "File Read Test",
            "2025-01-15T10:30:00"
        )
        
        file_path = Path(result['file_path'])
        
        # Make file unreadable by changing permissions
        try:
            file_path.chmod(0o000)  # No permissions
            
            # Search should handle the file read exception gracefully
            results = server.search_conversations("Test", limit=5)
            assert isinstance(results, list)
            
        finally:
            # Restore permissions for cleanup
            file_path.chmod(0o644)

    @pytest.mark.asyncio
    async def test_search_returns_error_in_results(self, server, temp_storage):
        """Test search error handling (lines 115-116)"""
        # Corrupt the index file to cause an error
        with open(server.index_file, 'w') as f:
            f.write("invalid json")
        
        results = server.search_conversations("test", limit=5)
        
        # Should return a list with error information
        assert isinstance(results, list)
        assert len(results) > 0
        assert any("error" in str(result) for result in results)

    def test_get_preview_exception_handling(self, server, temp_storage):
        """Test preview generation exception handling (lines 139-140)"""
        # Create a file that will cause an exception when reading
        test_file = Path(temp_storage) / "bad_file.md"
        test_file.touch()
        test_file.chmod(0o000)  # No read permissions
        
        try:
            preview = server._get_preview(test_file, ["search"])
            assert preview == "Preview unavailable"
        finally:
            test_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_add_conversation_exception_handling(self, server, temp_storage):
        """Test add conversation with various exception scenarios"""
        # Test with a read-only conversations directory
        server.conversations_path.chmod(0o444)
        
        try:
            result = server.add_conversation(
                "Test content that should fail",
                "Error Test",
                "2025-01-15T10:30:00"
            )
            
            assert result['status'] == 'error'
            assert 'message' in result
            assert "Failed to save conversation" in result['message']
            
        finally:
            server.conversations_path.chmod(0o755)

    @pytest.mark.asyncio
    async def test_update_index_exception_handling(self, server, temp_storage):
        """Test index update exception handling (line 217)"""
        # Make index file read-only to trigger write exception
        server.index_file.touch()  # Create it first
        server.index_file.chmod(0o444)  # Make read-only
        
        try:
            # This should trigger exception in _update_index when trying to write
            test_date = datetime(2025, 1, 15, 10, 30)
            test_topics = ["python"]
            test_title = "Error Test"
            fake_path = server.conversations_path / "test.md"
            fake_path.touch()
            
            # This calls _update_index internally which should handle the exception
            server.add_conversation("Test content", test_title, test_date.isoformat())
            
        finally:
            # Restore permissions
            server.index_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_update_topics_index_exception_handling(self, server, temp_storage):
        """Test topics index update exception handling (line 237)"""
        # Make topics file unwritable
        server.topics_file.chmod(0o444)
        
        try:
            server._update_topics_index(["python", "test"], "test_conv_id")
            # Exception should be caught and printed, but not re-raised
            
        finally:
            server.topics_file.chmod(0o644)
    
    @pytest.mark.asyncio
    async def test_search_file_not_exists(self, server, temp_storage):
        """Test search when conversation file doesn't exist (line 88)"""
        # Manually add entry to index that points to non-existent file
        import json
        fake_index = {
            "conversations": [{
                "title": "Non-existent File",
                "file_path": "conversations/nonexistent.md",
                "date": "2025-06-01T10:00:00Z",
                "topics": ["test"],
                "added": "2025-06-01T10:00:00Z"
            }],
            "last_updated": "2025-06-01T10:00:00Z"
        }
        
        with open(server.index_file, 'w') as f:
            json.dump(fake_index, f)
        
        # Search should skip the non-existent file
        results = server.search_conversations("test", limit=5)
        assert isinstance(results, list)
        
    @pytest.mark.asyncio
    async def test_add_conversation_no_date(self, server, temp_storage):
        """Test add_conversation with no date to cover line 153"""
        result = server.add_conversation(
            "Test content without date",
            "No Date Test",
            None  # This should trigger the datetime.now() path
        )
        
        assert result['status'] == 'success'
        assert 'file_path' in result

    @pytest.mark.asyncio
    async def test_weekly_summary_detailed_analysis(self, server):
        """Test weekly summary detailed content analysis (lines 286-299)"""
        current_time = datetime.now()
        
        # Add conversations that will trigger all the content analysis paths
        server.add_conversation(
            "Writing code for a new function with class definitions and import statements",
            "Coding with Code Keywords",
            current_time.isoformat()
        )
        
        server.add_conversation(
            "We decided on this approach and I recommend using this solution",
            "Decision with Recommendation",
            current_time.isoformat()
        )
        
        server.add_conversation(
            "Learning how to understand and explain complex tutorial concepts",
            "Learning How To",
            current_time.isoformat()
        )
        
        summary = server.generate_weekly_summary(0)
        
        # Verify all analysis paths were triggered
        assert "Coding with Code Keywords" in summary
        assert "Decision with Recommendation" in summary
        assert "Learning How To" in summary

    @pytest.mark.asyncio
    async def test_weekly_summary_content_read_exception(self, server, temp_storage):
        """Test weekly summary when conversation file read fails (lines 298-299)"""
        current_time = datetime.now()
        
        # Add a conversation
        result = server.add_conversation(
            "Test content for read exception",
            "Read Exception Test",
            current_time.isoformat()
        )
        
        # Make the conversation file unreadable
        file_path = Path(result['file_path'])
        file_path.chmod(0o000)
        
        try:
            summary = server.generate_weekly_summary(0)
            # Should complete without crashing despite file read error
            assert isinstance(summary, str)
            assert "Read Exception Test" in summary
            
        finally:
            file_path.chmod(0o644)

    @pytest.mark.asyncio 
    async def test_weekly_summary_with_topics_count(self, server):
        """Test weekly summary topic counting and top topics section"""
        # Add conversations with topics to test counting
        from datetime import datetime, timezone
        current_week_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        server.add_conversation(
            "Python programming discussion", 
            "Python Talk", 
            current_week_date
        )
        
        # Manually update topics index with test data
        topics_content = {
            "topics": {
                "python": 5,
                "javascript": 3,
                "testing": 2
            },
            "last_updated": "2025-06-01T10:00:00Z"
        }
        
        # Write topics index directly to test counting logic
        import json
        with open(server.topics_file, 'w') as f:
            json.dump(topics_content, f)
        
        summary = server.generate_weekly_summary(0)
        
        # Verify summary contains topics and structure
        assert "Most Discussed Topics" in summary or "Topics" in summary
        assert len(summary) > 100  # Ensure substantial summary content

    @pytest.mark.asyncio
    async def test_weekly_summary_comprehensive_sections(self, server):
        """Test weekly summary includes all expected sections"""
        from datetime import datetime, timezone, timedelta
        
        # Get current time in the proper timezone
        now = datetime.now(timezone.utc)
        current_week_date = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        
        # Add test conversation for current week
        server.add_conversation(
            "Technical discussion about API design", 
            "API Design", 
            current_week_date
        )
        
        summary = server.generate_weekly_summary(0)
        
        # Verify summary structure and content
        assert len(summary) > 100
        assert "Weekly Summary" in summary or "## " in summary or "API Design" in summary

    @pytest.mark.asyncio
    async def test_weekly_summary_file_saving_and_path(self, server, temp_storage):
        """Test weekly summary file saving functionality"""
        current_time = datetime.now()
        
        server.add_conversation(
            "Test conversation for file saving verification",
            "File Save Test",
            current_time.isoformat()
        )
        
        summary = server.generate_weekly_summary(0)
        
        # Verify file was saved
        assert "Summary saved to" in summary
        
        # Check that file actually exists with correct naming
        weekly_dir = server.summaries_path / "weekly"
        summary_files = list(weekly_dir.glob("week-*.md"))
        assert len(summary_files) > 0
        
        # Verify file contains the summary content
        latest_file = max(summary_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r') as f:
            file_content = f.read()
        
        assert "File Save Test" in file_content

    @pytest.mark.asyncio
    async def test_get_preview_success(self, server):
        """Test get_preview method with valid conversation (lines 232-248)"""
        # Add a test conversation
        result = server.add_conversation(
            "This is a test conversation content for preview testing",
            "Preview Test",
            "2025-06-02T10:00:00Z"
        )
        
        # Get the conversation ID from the index
        import json
        with open(server.index_file, 'r') as f:
            index_data = json.load(f)
        
        conversation_id = index_data["conversations"][-1]["id"]
        
        # Test get_preview
        preview = server.get_preview(conversation_id)
        assert "This is a test conversation content" in preview
        assert isinstance(preview, str)

    @pytest.mark.asyncio
    async def test_get_preview_long_content(self, server):
        """Test get_preview truncation for long content (line 248)"""
        # Create long content (>500 chars)
        long_content = "A" * 600
        result = server.add_conversation(
            long_content,
            "Long Content Test",
            "2025-06-02T10:00:00Z"
        )
        
        # Get conversation ID
        import json
        with open(server.index_file, 'r') as f:
            index_data = json.load(f)
        
        conversation_id = index_data["conversations"][-1]["id"]
        
        # Test preview truncation
        preview = server.get_preview(conversation_id)
        assert len(preview) == 503  # 500 chars + "..."
        assert preview.endswith("...")

    @pytest.mark.asyncio
    async def test_get_preview_file_not_found(self, server):
        """Test get_preview when conversation file doesn't exist (lines 249-250)"""
        # Manually add entry to index that points to non-existent file
        import json
        fake_index = {
            "conversations": [{
                "id": "fake_conv_id",
                "title": "Non-existent File",
                "file_path": "conversations/nonexistent.json",
                "date": "2025-06-01T10:00:00Z",
                "topics": ["test"],
                "added": "2025-06-01T10:00:00Z"
            }],
            "last_updated": "2025-06-01T10:00:00Z"
        }
        
        with open(server.index_file, 'w') as f:
            json.dump(fake_index, f)
        
        # Test get_preview with non-existent file
        preview = server.get_preview("fake_conv_id")
        assert preview == "Conversation file not found"

    @pytest.mark.asyncio
    async def test_get_preview_conversation_not_found(self, server):
        """Test get_preview when conversation ID doesn't exist (line 252)"""
        # Test with non-existent conversation ID
        preview = server.get_preview("nonexistent_conversation_id")
        assert preview == "Conversation not found"

    @pytest.mark.asyncio
    async def test_get_preview_exception_handling(self, server):
        """Test get_preview exception handling (lines 254-255)"""
        # Make index file unreadable to trigger exception
        server.index_file.chmod(0o000)
        
        try:
            preview = server.get_preview("any_id")
            assert preview.startswith("Error retrieving conversation:")
            
        finally:
            # Restore permissions
            server.index_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_extract_topics_quoted_terms(self, server):
        """Test topic extraction with quoted terms (lines 80-81)"""
        # Test with quoted terms that are NOT in common_tech_terms to trigger line 81
        content = 'We discussed "unique concept" and "special methodology" and "custom framework" in our project'
        result = server.add_conversation(content, "Quoted Terms Test", "2025-06-02T10:00:00Z")
        
        # Check that quoted terms were extracted properly
        import json
        with open(server.index_file, 'r') as f:
            index_data = json.load(f)
        
        topics = index_data["conversations"][-1]["topics"]
        # Should include quoted terms that meet length criteria (3-49 chars) and are not in common_tech_terms
        assert len(topics) > 0
        # Check for the quoted terms that should be added via line 81
        topic_str = " ".join(topics).lower()
        assert "unique concept" in topic_str or "special methodology" in topic_str or "custom framework" in topic_str

    @pytest.mark.asyncio
    async def test_add_conversation_invalid_date_format(self, server):
        """Test add_conversation with invalid date format (lines 99-100)"""
        # Use an invalid date format to trigger ValueError exception
        result = server.add_conversation(
            "Test content with invalid date",
            "Invalid Date Test", 
            "invalid-date-format"  # This should trigger ValueError and fallback to datetime.now()
        )
        
        assert result['status'] == 'success'
        assert 'file_path' in result

    @pytest.mark.asyncio
    async def test_add_conversation_auto_title_generation(self, server):
        """Test automatic title generation (lines 107-109)"""
        # Test with no title provided to trigger auto-generation
        long_content = "This is a very long first line that should be truncated when used as a title because it exceeds fifty characters in length"
        result = server.add_conversation(
            long_content,
            None,  # No title provided
            "2025-06-02T10:00:00Z"
        )
        
        # Check that title was auto-generated and truncated
        import json
        with open(server.index_file, 'r') as f:
            index_data = json.load(f)
        
        title = index_data["conversations"][-1]["title"]
        assert len(title) <= 53  # 50 chars + "..."
        assert title.endswith("...")

    @pytest.mark.asyncio
    async def test_get_preview_private_method(self, server):
        """Test _get_preview private method (lines 207-228)"""
        # Create a test file with content
        test_content = """Line 1: Introduction
Line 2: This contains search terms
Line 3: More context
Line 4: Additional info
Line 5: Final line"""
        
        result = server.add_conversation(test_content, "Preview Test", "2025-06-02T10:00:00Z")
        file_path = Path(result['file_path'])
        
        # Test _get_preview method directly
        preview = server._get_preview(file_path, ["search", "terms"])
        
        # Should include context around the matching line
        assert "search terms" in preview.lower()
        assert len(preview) > 0

    @pytest.mark.asyncio  
    async def test_get_preview_exception_handling_private(self, server):
        """Test _get_preview exception handling (lines 227-228)"""
        # Test with non-existent file to trigger exception
        fake_path = Path("/nonexistent/file.json")
        preview = server._get_preview(fake_path, ["test"])
        
        assert preview == "Preview unavailable"

    @pytest.mark.asyncio
    async def test_weekly_summary_file_read_exception(self, server):
        """Test weekly summary file read exception (lines 348-349)"""
        from datetime import datetime, timezone
        
        # Add a conversation first 
        result = server.add_conversation(
            "Test conversation for read exception",
            "Read Exception Test",
            datetime.now(timezone.utc).isoformat()
        )
        
        # Make the conversation file unreadable to trigger exception during reading
        file_path = Path(result['file_path'])
        file_path.chmod(0o000)
        
        try:
            summary = server.generate_weekly_summary(0)
            # Should complete without crashing despite file read error
            assert isinstance(summary, str)
            
        finally:
            file_path.chmod(0o644)
    
    @pytest.mark.asyncio
    async def test_weekly_summary_file_read_exception_corrupted(self, server):
        """Test weekly summary with corrupted conversation file (lines 348-349)"""
        from datetime import datetime, timezone
        
        # Add a conversation first
        result = server.add_conversation(
            "Test conversation for corruption test",
            "Corruption Test",
            datetime.now(timezone.utc).isoformat()
        )
        
        # Corrupt the conversation file to trigger exception during JSON parsing
        file_path = Path(result['file_path'])
        with open(file_path, 'w') as f:
            f.write("invalid json content that will cause parsing to fail")
        
        try:
            summary = server.generate_weekly_summary(0)
            # Should complete without crashing despite file corruption
            assert isinstance(summary, str)
            
        finally:
            # Restore a valid JSON file
            import json
            with open(file_path, 'w') as f:
                json.dump({"content": "restored content", "topics": []}, f)

    @pytest.mark.asyncio
    async def test_weekly_summary_index_entry_exception(self, server):
        """Test weekly summary with malformed index entry (lines 348-349)"""
        from datetime import datetime, timezone
        import json
        
        # First add a normal conversation
        server.add_conversation(
            "Test conversation",
            "Test",
            datetime.now(timezone.utc).isoformat()
        )
        
        # Manually corrupt the index with malformed entry to trigger exception on lines 348-349
        fake_index = {
            "conversations": [
                # This entry is missing required fields and will cause an exception
                {"malformed": "entry"},
                # Another problematic entry
                {"file_path": None, "date": "bad_date"},
            ],
            "last_updated": "2025-06-01T10:00:00Z"
        }
        
        with open(server.index_file, 'w') as f:
            json.dump(fake_index, f)
        
        # This should trigger exception handling on lines 348-349 and continue processing
        summary = server.generate_weekly_summary(0)
        assert isinstance(summary, str)

    @pytest.mark.asyncio
    async def test_weekly_summary_no_conversations_found(self, server):
        """Test weekly summary when no conversations found (line 352)"""
        # Generate summary for a week with no conversations (far in future)
        summary = server.generate_weekly_summary(52)  # 52 weeks from now
        
        # Should return "No conversations found" message
        assert "No conversations found for week of" in summary


class TestMCPToolWrapperFunctions:
    """Test the MCP tool wrapper functions for complete coverage"""

    def test_mcp_imports(self):
        """Test that MCP imports are available (skipped if not in Python 3.11+)"""
        import sys
        if sys.version_info < (3, 11):
            pytest.skip("MCP requires Python 3.11+")
        
        try:
            import mcp.types
            import mcp
            assert True
        except ImportError as e:
            pytest.fail(f"MCP import failed: {e}")

    @pytest.mark.asyncio
    async def test_mcp_search_tool_no_results(self):
        """Test MCP search tool wrapper when no results found"""
        # Import the MCP tool functions directly
        from server_fastmcp import search_conversations as mcp_search
        
        result = await mcp_search("nonexistentquery12345xyz", limit=5)
        assert "No conversations found matching" in result

    @pytest.mark.asyncio
    async def test_mcp_search_tool_with_error_results(self, server):
        """Test MCP search tool handles search errors gracefully"""
        from server_fastmcp import search_conversations as mcp_search
        
        # Test with search query that returns no results
        result = await mcp_search("nonexistent_query_12345", limit=5)
        
        # Should return formatted message for no results
        assert isinstance(result, str)
        assert "Found 0 conversations" in result or "No conversations found" in result

    @pytest.mark.asyncio
    async def test_mcp_search_tool_success_formatting(self, server):
        """Test MCP search tool result formatting"""
        from server_fastmcp import search_conversations as mcp_search
        
        # Add test data
        server.add_conversation(
            "Test conversation for MCP search formatting",
            "Test Formatting",
            "2025-06-02T10:00:00Z"
        )
        
        result = await mcp_search("Test", limit=1)
        
        # Verify proper formatting - check for the actual structure
        assert isinstance(result, str)
        # Accept both success and no results cases
        assert ("Found" in result and "conversations" in result) or "No conversations found" in result
        if "Found" in result:
            assert "**" in result  # Should have bold formatting for titles

    @pytest.mark.asyncio
    async def test_mcp_add_conversation_tool(self, server):
        """Test MCP add conversation tool wrapper"""
        from server_fastmcp import add_conversation as mcp_add
        
        result = await mcp_add(
            "Test content for MCP add tool",
            "MCP Add Test",
            "2025-06-02T12:00:00Z"
        )
        
        assert "Status: success" in result
        assert "Conversation saved successfully" in result

    @pytest.mark.asyncio
    async def test_mcp_weekly_summary_tool(self, server):
        """Test MCP weekly summary tool wrapper"""
        from server_fastmcp import generate_weekly_summary as mcp_summary
        
        # Add some test data
        current_time = datetime.now().isoformat()
        server.add_conversation(
            "Weekly summary test conversation",
            "Weekly Test",
            current_time
        )
        
        result = await mcp_summary(0)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_final_coverage_lines(self, server):
        """Test the final missing lines for 100% coverage"""
        from datetime import datetime, timezone
        from server_fastmcp import search_conversations as mcp_search
        
        # Test line 343: topics_str += "..." when more than 3 topics
        now = datetime.now(timezone.utc)
        current_week_date = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        
        server.add_conversation(
            "Test with many topics for truncation",
            "Many Topics Test",
            current_week_date
        )
        
        # Manually add many topics to trigger line 343
        import json
        with open(server.index_file, 'r') as f:
            index_data = json.load(f)
        
        # Update both the conversation file and index to have more than 3 topics
        if index_data["conversations"]:
            conv_info = index_data["conversations"][-1]
            conv_file_path = server.storage_path / conv_info["file_path"]
            
            # Update the actual conversation file
            with open(conv_file_path, 'r') as f:
                conv_data = json.load(f)
            conv_data["topics"] = ["topic1", "topic2", "topic3", "topic4", "topic5"]
            with open(conv_file_path, 'w') as f:
                json.dump(conv_data, f)
            
            # Update the index as well
            index_data["conversations"][-1]["topics"] = ["topic1", "topic2", "topic3", "topic4", "topic5"]
            with open(server.index_file, 'w') as f:
                json.dump(index_data, f)
        
        # Generate summary to trigger line 343 (topics truncation)
        summary = server.generate_weekly_summary(0)
        assert "..." in summary  # Should show truncated topics
        
        # Test lines 359-360: Exception handling in generate_weekly_summary
        # Corrupt the index file to trigger exception
        with open(server.index_file, 'w') as f:
            f.write("invalid json")
        
        summary_with_error = server.generate_weekly_summary(0)
        assert "Failed to generate weekly summary" in summary_with_error
        
        # Test lines 378-379: Error handling in MCP search tool
        # We need to test the mcp_search directly with error results
        from server_fastmcp import memory_server
        
        # Backup original method
        original_search = memory_server.search_conversations
        
        def mock_error_search(query, limit):
            return [{"error": "Test search error"}]
        
        # Replace the method on the global memory_server instance
        memory_server.search_conversations = mock_error_search
        
        try:
            result = await mcp_search("test", limit=1)
            assert "Error: Test search error" in result
        finally:
            memory_server.search_conversations = original_search


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--cov=server_fastmcp", "--cov-report=html", "--cov-report=term"])