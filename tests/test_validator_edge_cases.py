#!/usr/bin/env python3
"""
Test module for validator edge cases to achieve 100% coverage.

This module specifically targets line 104 in validators.py 
which handles content that's too short.
"""

import unittest
from pathlib import Path

# Add project root and src directory to path using dynamic resolution
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from validators import validate_content, ContentValidationError


class TestValidatorEdgeCases(unittest.TestCase):
    """Test edge cases in validators.py for complete coverage"""
    
    def test_content_validation_logic(self):
        """Test content validation logic and document unreachable code"""
        # Test that line 104 is unreachable due to MIN_CONTENT_LENGTH = 1
        # Any content with len < 1 is empty and caught by line 99 first
        
        # Empty content should trigger line 99, not line 104
        with self.assertRaises(ContentValidationError) as context:
            validate_content("")
        
        self.assertIn("Content cannot be empty", str(context.exception))
        # This confirms line 104 is unreachable for MIN_CONTENT_LENGTH = 1
    
    def test_content_at_minimum_length(self):
        """Test content at exactly minimum length"""
        # Test content at minimum length (should pass)
        min_content = "a"  # 1 character, minimum length
        
        # This should not raise an exception
        try:
            validate_content(min_content)
        except ContentValidationError:
            self.fail("Content at minimum length should be valid")
    
    def test_whitespace_only_content(self):
        """Test content that's only whitespace"""
        # Test content that's only whitespace 
        whitespace_content = "   "  # Whitespace only - truthy but effectively empty
        
        # Should be valid since it's not empty (length > 0) and passes all checks
        try:
            result = validate_content(whitespace_content)
            self.assertEqual(result, whitespace_content)  # Should return as-is
        except ContentValidationError:
            self.fail("Whitespace content should be valid (not empty)")


if __name__ == '__main__':
    unittest.main()