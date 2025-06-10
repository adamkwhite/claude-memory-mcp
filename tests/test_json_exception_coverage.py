#!/usr/bin/env python3
"""
Test module for JSON exception handling coverage in conversation_memory.py.

This module specifically targets lines 353-354 in conversation_memory.py
which handle JSON processing errors in the get_week_conversations method.
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open

# Add project root and src directory to path using dynamic resolution
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from conversation_memory import ConversationMemoryServer


class TestJSONExceptionCoverage(unittest.TestCase):
    """Test JSON exception handling in conversation_memory.py"""
    
    def setUp(self):
        """Set up test environment with temporary storage"""
        self.temp_dir = tempfile.mkdtemp(prefix="test_json_coverage_")
        self.storage_path = Path(self.temp_dir)
        self.memory = ConversationMemoryServer(str(self.storage_path))
    
    def test_get_week_conversations_invalid_json(self):
        """Test exception handling for invalid JSON in index file (lines 353-354)"""
        # Create an invalid JSON file that will trigger ValueError during json.load()
        index_file = self.storage_path / "conversations" / "index.json"
        index_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write invalid JSON that will cause json.load() to raise ValueError
        with open(index_file, 'w') as f:
            f.write('{"conversations": [invalid json content}')  # Invalid JSON syntax
        
        # This should trigger the exception handling on lines 353-354
        start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 7)
        result = self.memory._get_week_conversations(start_date, end_date)
        
        # Should return empty list when JSON parsing fails
        self.assertEqual(result, [])
    
    def test_get_week_conversations_missing_key(self):
        """Test exception handling for missing key in JSON (lines 353-354)"""
        # Create valid JSON but with missing expected structure
        index_file = self.storage_path / "conversations" / "index.json"
        index_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Valid JSON but missing 'conversations' key structure that triggers KeyError
        with open(index_file, 'w') as f:
            json.dump({"wrong_key": "value"}, f)
        
        # This should trigger the KeyError handling on lines 353-354
        start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 7)
        result = self.memory._get_week_conversations(start_date, end_date)
        
        # Should return empty list when key structure is wrong
        self.assertEqual(result, [])
    
    def test_get_week_conversations_wrong_type(self):
        """Test exception handling for wrong data type (lines 353-354)"""
        # Create JSON with wrong data type that will trigger TypeError
        index_file = self.storage_path / "conversations" / "index.json"
        index_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Valid JSON but conversations is not a list (wrong type)
        with open(index_file, 'w') as f:
            json.dump({"conversations": "not_a_list"}, f)
        
        # This should trigger TypeError when trying to iterate
        start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 7)
        result = self.memory._get_week_conversations(start_date, end_date)
        
        # Should return empty list when data types are wrong
        self.assertEqual(result, [])
    
    def test_get_week_conversations_file_not_found(self):
        """Test exception handling for missing index file (lines 353-354)"""
        # Don't create the index file - this will trigger OSError
        # This should trigger the OSError handling on lines 353-354
        start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 7)
        result = self.memory._get_week_conversations(start_date, end_date)
        
        # Should return empty list when file doesn't exist
        self.assertEqual(result, [])
    
    def test_get_week_conversations_permission_error(self):
        """Test exception handling for file permission errors (lines 353-354)"""
        # Create index file but mock permission error
        index_file = self.storage_path / "conversations" / "index.json"
        index_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(index_file, 'w') as f:
            json.dump({"conversations": []}, f)
        
        # Mock open to raise PermissionError (subclass of OSError)
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 7)
        result = self.memory._get_week_conversations(start_date, end_date)
            
        # Should return empty list when file can't be read
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()