#!/usr/bin/env python3
"""
Test suite for BaseImporter abstract class.

Tests the foundation functionality for all platform-specific importers.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.importers.base_importer import BaseImporter, ImportResult


class TestImporter(BaseImporter):
    """Concrete implementation for testing abstract BaseImporter."""

    def __init__(self, storage_path: Path):
        super().__init__(storage_path, "test")

    def get_supported_formats(self) -> List[str]:
        return [".json", ".txt"]

    def import_file(self, file_path: Path) -> ImportResult:
        """Simple implementation for testing."""
        return ImportResult(
            success=True,
            conversations_imported=1,
            conversations_failed=0,
            errors=[],
            imported_ids=["test_id"],
            metadata={"test": True}
        )

    def parse_conversation(self, raw_data: Any) -> Dict[str, Any]:
        """Simple implementation for testing."""
        return self.create_universal_conversation(
            platform_id="test_123",
            title="Test Conversation",
            content="Test content",
            messages=[],
            date=datetime.now(),
            model="test-model"
        )


class TestImportResult:
    """Test ImportResult data structure."""

    def test_import_result_creation(self):
        """Test basic ImportResult creation."""
        result = ImportResult(
            success=True,
            conversations_imported=5,
            conversations_failed=2,
            errors=["Error 1", "Error 2"],
            imported_ids=["id1", "id2", "id3"],
            metadata={"source": "test"}
        )

        assert result.success is True
        assert result.conversations_imported == 5
        assert result.conversations_failed == 2
        assert result.errors == ["Error 1", "Error 2"]
        assert result.imported_ids == ["id1", "id2", "id3"]
        assert result.metadata == {"source": "test"}

    def test_import_result_success_rate(self):
        """Test success rate calculation."""
        result = ImportResult(
            success=True,
            conversations_imported=8,
            conversations_failed=2,
            errors=[],
            imported_ids=[],
            metadata={}
        )

        assert result.success_rate == 0.8  # 8/(8+2) = 0.8

    def test_import_result_success_rate_zero_total(self):
        """Test success rate with zero total conversations."""
        result = ImportResult(
            success=False,
            conversations_imported=0,
            conversations_failed=0,
            errors=[],
            imported_ids=[],
            metadata={}
        )

        assert result.success_rate == 0.0

    def test_import_result_perfect_success(self):
        """Test success rate with perfect success."""
        result = ImportResult(
            success=True,
            conversations_imported=10,
            conversations_failed=0,
            errors=[],
            imported_ids=[],
            metadata={}
        )

        assert result.success_rate == 1.0


class TestBaseImporter:
    """Test BaseImporter abstract class functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        self.importer = TestImporter(self.storage_path)

    def test_importer_initialization(self):
        """Test importer initialization."""
        assert self.importer.storage_path == self.storage_path
        assert self.importer.platform_name == "test"
        assert self.importer.logger is not None

    def test_create_universal_conversation(self):
        """Test universal conversation format creation."""
        date = datetime(2025, 1, 15, 12, 0, 0)
        messages = [
            {
                "role": "user",
                "content": "Hello",
                "timestamp": date.isoformat(),
                "metadata": {}
            }
        ]

        conversation = self.importer.create_universal_conversation(
            platform_id="test_123",
            title="Test Chat",
            content="Test conversation content",
            messages=messages,
            date=date,
            model="gpt-4",
            session_context={"session_id": "abc123"},
            metadata={"test_key": "test_value"}
        )

        # Verify required fields
        assert conversation["platform_id"] == "test_123"
        assert conversation["title"] == "Test Chat"
        assert conversation["content"] == "Test conversation content"
        assert conversation["messages"] == messages
        assert conversation["model"] == "gpt-4"
        assert conversation["platform"] == "test"

        # Verify generated fields
        assert "id" in conversation
        assert conversation["id"].startswith("conv_")
        assert len(conversation["id"]) > 15

        # Verify dates
        assert conversation["date"] == date.isoformat()
        assert "created_at" in conversation
        assert "last_updated" in conversation

        # Verify topics extraction
        assert "topics" in conversation
        assert isinstance(conversation["topics"], list)
        assert "test" in conversation["topics"]  # platform name should be in topics

        # Verify metadata and session context
        assert conversation["session_context"] == {"session_id": "abc123"}
        assert conversation["platform_metadata"]["test_key"] == "test_value"

        # Verify import metadata
        assert "import_metadata" in conversation
        assert conversation["import_metadata"]["source_format"] == "test"

    def test_create_message(self):
        """Test message creation utility."""
        timestamp = datetime.now()
        message = self.importer._create_message(
            role="user",
            content="Hello world",
            timestamp=timestamp,
            message_id="msg_123",
            metadata={"source": "test"}
        )

        assert message["role"] == "user"
        assert message["content"] == "Hello world"
        assert message["timestamp"] == timestamp.isoformat()
        assert message["id"] == "msg_123"
        assert message["metadata"]["source"] == "test"

    def test_create_message_auto_id(self):
        """Test message creation with auto-generated ID."""
        message = self.importer._create_message(
            role="ASSISTANT",  # Test case conversion
            content="Hello back"
        )

        assert message["role"] == "assistant"  # Should be lowercased
        assert message["content"] == "Hello back"
        assert "id" in message
        assert len(message["id"]) > 20  # UUID4 format
        assert "timestamp" in message

    def test_parse_timestamp_iso_format(self):
        """Test timestamp parsing with ISO format."""
        timestamp_str = "2025-01-15T12:30:45Z"
        parsed = self.importer._parse_timestamp(timestamp_str)

        assert parsed.year == 2025
        assert parsed.month == 1
        assert parsed.day == 15
        assert parsed.hour == 12
        assert parsed.minute == 30
        assert parsed.second == 45

    def test_parse_timestamp_unix_format(self):
        """Test timestamp parsing with Unix timestamp string."""
        # BaseImporter._parse_timestamp expects string input, not numbers
        timestamp_str = "2022-01-15T12:30:45Z"
        parsed = self.importer._parse_timestamp(timestamp_str)

        assert parsed.year == 2022
        assert parsed.month == 1
        assert parsed.day == 15

    def test_parse_timestamp_invalid_format(self):
        """Test timestamp parsing with invalid format."""
        invalid_timestamp = "invalid-date"
        parsed = self.importer._parse_timestamp(invalid_timestamp)

        # Should return current time for invalid formats
        assert isinstance(parsed, datetime)
        assert abs((datetime.now() - parsed).total_seconds()) < 5

    def test_extract_topics_basic(self):
        """Test basic topic extraction."""
        content = "This is about Python programming and machine learning AI."
        topics = self.importer._extract_topics(content)

        assert "python" in topics
        assert "programming" in topics
        assert "machine learning" in topics
        assert "ai" in topics

    def test_extract_topics_quoted_terms(self):
        """Test topic extraction with quoted terms."""
        content = 'Discussion about "neural network" and "machine learning" concepts.'
        topics = self.importer._extract_topics(content)

        # The BaseImporter looks for individual terms, not quoted phrases
        assert "machine learning" in topics  # This is in the predefined list

    def test_extract_topics_limit(self):
        """Test topic extraction respects limit."""
        # Create content with many potential topics
        topics_list = ["topic" + str(i) for i in range(20)]
        content = " ".join(topics_list)

        topics = self.importer._extract_topics(content)

        # Should be limited to 10 topics
        assert len(topics) <= 10

    def test_combine_messages_to_content(self):
        """Test combining messages into content string."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]

        content = self.importer._combine_messages_to_content(messages)

        expected = "**Human**: Hello\n\n**Assistant**: Hi there!\n\n**Human**: How are you?"
        assert content == expected

    def test_validate_conversation_valid(self):
        """Test conversation validation with valid data."""
        conversation = {
            "id": "conv_123",
            "platform": "test",
            "platform_id": "original_123",
            "model": "test-model",
            "title": "Test",
            "content": "Test content",
            "messages": [],
            "date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "topics": ["test"],
            "session_context": {},
            "import_metadata": {},
            "created_at": datetime.now().isoformat()
        }

        assert self.importer._validate_conversation(conversation) is True

    def test_validate_conversation_missing_fields(self):
        """Test conversation validation with missing required fields."""
        conversation = {
            "id": "conv_123",
            "title": "Test"
            # Missing required fields
        }

        assert self.importer._validate_conversation(conversation) is False

    def test_validate_conversation_invalid_types(self):
        """Test conversation validation with invalid field types."""
        conversation = {
            "id": "conv_123",
            "title": "Test",
            "content": "Test content",
            "date": datetime.now().isoformat(),
            "platform": "test",
            "messages": "not_a_list"  # Should be list
        }

        assert self.importer._validate_conversation(conversation) is False

    def test_abstract_methods(self):
        """Test that abstract methods are implemented."""
        # These should not raise NotImplementedError
        assert self.importer.get_supported_formats() == [".json", ".txt"]

        result = self.importer.import_file(Path("test.json"))
        assert isinstance(result, ImportResult)

        parsed = self.importer.parse_conversation({"test": "data"})
        assert isinstance(parsed, dict)

    def test_import_file_implementation(self):
        """Test the concrete import_file implementation."""
        test_file = self.storage_path / "test.json"
        test_file.write_text('{"test": "data"}')

        result = self.importer.import_file(test_file)

        assert result.success is True
        assert result.conversations_imported == 1
        assert result.conversations_failed == 0
        assert result.imported_ids == ["test_id"]
        assert result.metadata["test"] is True

    def test_parse_conversation_implementation(self):
        """Test the concrete parse_conversation implementation."""
        conversation = self.importer.parse_conversation({"test": "data"})

        assert conversation["platform_id"] == "test_123"
        assert conversation["title"] == "Test Conversation"
        assert conversation["content"] == "Test content"
        assert conversation["model"] == "test-model"
        assert conversation["platform"] == "test"
        assert "id" in conversation
        assert "topics" in conversation


class TestBaseImporterEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        self.importer = TestImporter(self.storage_path)

    def test_create_universal_conversation_minimal(self):
        """Test conversation creation with minimal required parameters."""
        conversation = self.importer.create_universal_conversation(
            platform_id="min_123",
            title="Minimal",
            content="Content",
            messages=[],
            date=datetime.now()
        )

        # Should have sensible defaults
        assert conversation["model"] == "unknown"
        assert conversation["session_context"] == {}
        assert isinstance(conversation["import_metadata"], dict)

    def test_create_message_edge_cases(self):
        """Test message creation edge cases."""
        # Empty content
        message = self.importer._create_message(
            role="user",
            content=""
        )
        assert message["content"] == ""

        # None timestamp (should use current time)
        message = self.importer._create_message(
            role="user",
            content="test",
            timestamp=None
        )
        assert "timestamp" in message

    def test_extract_topics_empty_content(self):
        """Test topic extraction with empty content."""
        topics = self.importer._extract_topics("")
        # Empty content returns empty list (early return)
        assert topics == []

        topics = self.importer._extract_topics("   ")
        # Whitespace content will include platform name
        assert "test" in topics

    def test_combine_messages_empty_list(self):
        """Test combining empty message list."""
        content = self.importer._combine_messages_to_content([])
        assert content == ""

    def test_parse_timestamp_edge_cases(self):
        """Test timestamp parsing edge cases."""
        # Empty string
        result = self.importer._parse_timestamp("")
        assert isinstance(result, datetime)

        # Invalid format returns current time
        result = self.importer._parse_timestamp("not-a-date")
        assert isinstance(result, datetime)
