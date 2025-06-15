#!/usr/bin/env python3
"""
Test suite for ClaudeImporter.

Tests Claude conversation import functionality for various export formats.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from src.importers.claude_importer import ClaudeImporter
from src.importers.base_importer import ImportResult


class TestClaudeImporter:
    """Test ClaudeImporter core functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        self.importer = ClaudeImporter(self.storage_path)
    
    def test_importer_initialization(self):
        """Test ClaudeImporter initialization."""
        importer = ClaudeImporter(self.storage_path)
        assert importer.storage_path == self.storage_path
        assert importer.platform_name == "claude"
        assert importer.logger is not None
    
    def test_get_supported_formats(self):
        """Test supported file formats."""
        formats = self.importer.get_supported_formats()
        expected_formats = [".json", ".md", ".txt"]
        for fmt in expected_formats:
            assert fmt in formats
    
    def test_import_file_nonexistent(self):
        """Test importing non-existent file."""
        non_existent = self.storage_path / "does_not_exist.json"
        result = self.importer.import_file(non_existent)
        
        assert result.success is False
        assert result.conversations_imported == 0
        assert result.conversations_failed == 1
        assert "File not found" in result.errors[0]
    
    def test_import_file_general_exception(self):
        """Test import with general exception."""
        test_file = self.storage_path / "test.json"
        test_file.write_text('{"test": "data"}')
        
        with patch.object(self.importer, '_import_json_format', side_effect=Exception("Test error")):
            result = self.importer.import_file(test_file)
        
        assert result.success is False
        assert result.conversations_imported == 0
        assert result.conversations_failed == 1
        assert "Import failed" in result.errors[0]


class TestClaudeImporterJSONFormat:
    """Test ClaudeImporter JSON format handling."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        self.importer = ClaudeImporter(self.storage_path)
    
    def test_import_claude_memory_format(self):
        """Test importing existing Claude Memory format."""
        memory_data = {
            "id": "conv_20250115_120000_abcd1234",
            "platform": "claude",
            "title": "Test Claude Memory Conversation",
            "content": "**Human**: Hello Claude\n\n**Claude**: Hello! How can I help you?",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello Claude",
                    "timestamp": "2025-01-15T12:00:00Z"
                },
                {
                    "role": "assistant", 
                    "content": "Hello! How can I help you?",
                    "timestamp": "2025-01-15T12:01:00Z"
                }
            ],
            "date": "2025-01-15T12:00:00Z",
            "topics": ["greeting"],
            "created_at": "2025-01-15T12:00:00Z"
        }
        
        test_file = self.storage_path / "claude_memory.json"
        test_file.write_text(json.dumps(memory_data))
        
        result = self.importer.import_file(test_file)
        
        assert result.success is True
        assert result.conversations_imported == 1
        assert result.conversations_failed == 0
        assert result.metadata["format"] == "claude_memory"
        assert result.metadata["already_imported"] is True
        assert result.imported_ids == ["conv_20250115_120000_abcd1234"]
    
    def test_import_json_invalid_format(self):
        """Test importing invalid JSON."""
        test_file = self.storage_path / "invalid.json"
        test_file.write_text('{"invalid": json syntax}')
        
        result = self.importer.import_file(test_file)
        
        assert result.success is False
        assert result.conversations_imported == 0
        assert result.conversations_failed == 1
        assert "Invalid JSON format" in result.errors[0]
    
    def test_import_json_unsupported_format(self):
        """Test importing JSON with unsupported Claude format."""
        unsupported_data = {"not_claude": "data", "random": "fields"}
        
        test_file = self.storage_path / "unsupported.json"
        test_file.write_text(json.dumps(unsupported_data))
        
        result = self.importer.import_file(test_file)
        
        # Should successfully import as generic Claude JSON
        assert result.success is True
        assert result.conversations_imported == 1
        assert result.conversations_failed == 0
        assert result.metadata["format"] == "claude_generic_json"


class TestClaudeImporterTextFormat:
    """Test ClaudeImporter text format handling."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        self.importer = ClaudeImporter(self.storage_path)
    
    def test_import_claude_web_markdown(self):
        """Test importing Claude web interface markdown."""
        markdown_content = """# Conversation with Claude

**Human**: Hello Claude, how are you today?

**Claude**: Hello! I'm doing well, thank you for asking. I'm here and ready to help with any questions or tasks you might have. How are you doing today?
"""
        
        test_file = self.storage_path / "claude_web.md"
        test_file.write_text(markdown_content)
        
        with patch.object(self.importer, '_save_conversation') as mock_save:
            result = self.importer.import_file(test_file)
        
        assert result.success is True
        assert result.conversations_imported == 1
        assert result.conversations_failed == 0
        mock_save.assert_called_once()
    
    def test_import_text_exception(self):
        """Test text import with exception."""
        test_file = self.storage_path / "test.txt"
        test_file.write_text("Test content")
        
        with patch.object(self.importer, '_import_text_format', side_effect=Exception("Parse error")):
            result = self.importer.import_file(test_file)
        
        assert result.success is False
        assert result.conversations_imported == 0
        assert result.conversations_failed == 1
        assert "Import failed" in result.errors[0]


class TestClaudeImporterParsingMethods:
    """Test ClaudeImporter parsing methods."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        self.importer = ClaudeImporter(self.storage_path)
    
    def test_parse_conversation_dict(self):
        """Test parsing dict as conversation."""
        data = {
            "title": "Test Conv",
            "content": "Test content",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        result = self.importer.parse_conversation(data)
        
        assert result["platform"] == "claude"
        assert result["title"] == "Test Conv"
        assert len(result["messages"]) == 1
    
    def test_parse_conversation_invalid_type(self):
        """Test parsing invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Claude conversation data must be"):
            self.importer.parse_conversation(123)
    
    def test_detect_claude_format_memory(self):
        """Test Claude Memory format detection."""
        data = {
            "id": "conv_20250115_120000_abcd",
            "platform": "claude",
            "content": "test",
            "messages": [],
            "topics": [],
            "created_at": "2025-01-15"
        }
        
        result = self.importer._is_claude_memory_format(data)
        assert result is True
    
    def test_detect_claude_format_unknown(self):
        """Test unknown format detection."""
        data = {"random": "data"}
        
        result = self.importer._is_claude_memory_format(data)
        assert result is False


class TestClaudeImporterSaveConversation:
    """Test ClaudeImporter conversation saving."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        self.importer = ClaudeImporter(self.storage_path)
    
    def test_save_conversation(self):
        """Test saving conversation to storage."""
        conversation = {
            "id": "claude_20250115_120000_abcd1234",
            "date": "2025-01-15T12:00:00",
            "title": "Test Claude Conversation",
            "content": "Test content",
            "platform": "claude"
        }
        
        file_path = self.importer._save_conversation(conversation)
        
        # Verify file was created
        assert file_path.exists()
        assert "2025" in str(file_path)
        assert "01-january" in str(file_path)
        assert file_path.name.endswith(".json")
        
        # Verify content
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["id"] == conversation["id"]
        assert saved_data["platform"] == "claude"


class TestClaudeImporterIntegration:
    """Test ClaudeImporter integration scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir)
        self.importer = ClaudeImporter(self.storage_path)
    
    def test_end_to_end_claude_memory_import(self):
        """Test complete end-to-end Claude Memory import workflow."""
        claude_data = {
            "id": "conv_20250115_090000_e2etest",
            "platform": "claude",
            "title": "E2E Claude Memory Test",
            "content": "**Human**: Test the Claude importer\n\n**Claude**: Testing the Claude Memory import functionality.",
            "messages": [
                {
                    "role": "user",
                    "content": "Test the Claude importer",
                    "timestamp": "2025-01-15T09:00:00Z"
                },
                {
                    "role": "assistant",
                    "content": "Testing the Claude Memory import functionality.",
                    "timestamp": "2025-01-15T09:01:00Z"
                }
            ],
            "date": "2025-01-15T09:00:00Z",
            "topics": ["testing", "import"],
            "created_at": "2025-01-15T09:00:00Z"
        }
        
        test_file = self.storage_path / "claude_e2e_test.json"
        test_file.write_text(json.dumps(claude_data))
        
        result = self.importer.import_file(test_file)
        
        # Verify import success
        assert result.success is True
        assert result.conversations_imported == 1
        assert result.conversations_failed == 0
        assert len(result.imported_ids) == 1
        
        # Verify metadata
        assert result.metadata["platform"] == "claude"
        assert result.metadata["source_file"] == str(test_file)
        
        # Verify conversation file was created (excludes source file)
        conversation_files = [f for f in self.storage_path.rglob("*.json") if f.name != "claude_e2e_test.json"]
        assert len(conversation_files) == 1
        
        # Verify conversation content
        with open(conversation_files[0], 'r') as f:
            saved_conversation = json.load(f)
        
        assert saved_conversation["platform"] == "claude"
        assert saved_conversation["id"] == "conv_20250115_090000_e2etest"
        assert len(saved_conversation["messages"]) == 2
        assert "Claude Memory import" in saved_conversation["content"]