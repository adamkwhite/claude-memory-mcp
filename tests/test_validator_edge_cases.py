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
    
    def test_content_too_short_validation(self):
        """Test content too short validation (line 104)"""
        # Test empty content which is below minimum length of 1
        short_content = ""  # 0 characters, below minimum of 1
        
        with self.assertRaises(ContentValidationError) as context:
            validate_content(short_content)
        
        # Verify the specific error message from line 104
        self.assertIn("Content too short:", str(context.exception))
        self.assertIn("characters (min", str(context.exception))
    
    def test_content_at_minimum_length(self):
        """Test content at exactly minimum length"""
        # Test content at minimum length (should pass)
        min_content = "a"  # 1 character, minimum length
        
        # This should not raise an exception
        try:
            validate_content(min_content)
        except ContentValidationError:
            self.fail("Content at minimum length should be valid")
    
    def test_content_zero_length_after_strip(self):
        """Test content that becomes empty after stripping whitespace"""
        # Test content that's only whitespace (should be caught by empty check first)
        whitespace_content = "   "  # Whitespace only
        
        with self.assertRaises(ContentValidationError) as context:
            validate_content(whitespace_content)
        
        # This might trigger empty content error or short content error
        error_msg = str(context.exception)
        self.assertTrue("Content cannot be empty" in error_msg or "Content too short" in error_msg)


if __name__ == '__main__':
    unittest.main()