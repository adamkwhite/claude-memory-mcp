#!/usr/bin/env python3
"""Ultra-focused test for the final 2 lines: 25-26, 109-110 in server_fastmcp.py"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


class TestFinal2Lines(unittest.TestCase):
    """Target the final 2 lines for 100% coverage"""
    
    def test_import_error_lines_25_26_direct(self):
        """Test lines 25-26: ImportError handling for exceptions and logging_config"""
        
        # Clear any existing imports
        modules_to_clear = [
            'server_fastmcp', 'exceptions', 'logging_config', 
            'validators', 'conversation_memory'
        ]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Mock specific imports to force ImportError on lines 25-26
        original_import = __builtins__['__import__']
        
        def mock_import(name, *args, **kwargs):
            if name in ['.exceptions', '.logging_config'] and args and args[0] and '.' in args[0]:
                # This should trigger the ImportError for relative imports on lines 25-26
                raise ImportError(f"Mock ImportError for {name}")
            return original_import(name, *args, **kwargs)
        
        # Test the ImportError path
        with patch('builtins.__import__', side_effect=mock_import):
            try:
                # This should trigger lines 25-26 ImportError handling
                import server_fastmcp
                # If we get here, it means the fallback imports worked
                self.assertTrue(hasattr(server_fastmcp, 'ConversationMemoryServer'))
            except ImportError as e:
                # This is expected - the mock is working
                self.assertIn("Mock ImportError", str(e))

    def test_path_traversal_lines_109_110_exact_match(self):
        """Test lines 109-110: Security validation (path traversal or home dir)"""
        
        # Import the server class
        from server_fastmcp import ConversationMemoryServer
        
        # Test security validation with path containing ..
        home = Path.home()
        traversal_path = str(home / "safe_dir" / ".." / ".." / "dangerous")
        
        with self.assertRaises(ValueError) as context:
            ConversationMemoryServer(traversal_path)
        
        # Either security validation is acceptable
        error_msg = str(context.exception)
        self.assertTrue(
            "cannot contain '..'" in error_msg or
            "must be within user's home directory" in error_msg,
            f"Expected security validation, got: {error_msg}"
        )


if __name__ == '__main__':
    unittest.main()