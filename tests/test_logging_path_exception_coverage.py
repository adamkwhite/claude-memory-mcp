#!/usr/bin/env python3
"""
Test module for path operation exception handling in logging_config.py.

This module targets the final logging exception paths related to path operations
and redaction failures in security logging and file operation logging.
"""

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root and src directory to path using dynamic resolution
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from logging_config import log_security_event, log_file_operation


class TestLoggingPathExceptionCoverage(unittest.TestCase):
    """Test path operation exception handling in logging_config.py"""
    
    def test_security_event_path_redaction_failure_lines_147_149(self):
        """Test log_security_event path redaction failure (lines 147-149)"""
        # Mock Path operations to raise ValueError during path redaction
        with patch('pathlib.Path.is_absolute', side_effect=ValueError("Path operation failed")):
            # This should trigger the ValueError/OSError handling in lines 147-149
            try:
                log_security_event(
                    "PATH_TEST", 
                    "Testing path /sensitive/path/that/should/be/redacted", 
                    "ERROR"
                )
                # Should not raise an exception - should use fallback path redaction
            except Exception as e:
                self.fail(f"log_security_event should handle path operation errors, but raised: {e}")
    
    def test_security_event_path_redaction_os_error_lines_147_149(self):
        """Test log_security_event path redaction OSError (lines 147-149)"""
        # Mock Path operations to raise OSError during path redaction  
        with patch('pathlib.Path.is_relative_to', side_effect=OSError("File system error")):
            # This should trigger the OSError handling in lines 147-149
            try:
                log_security_event(
                    "PATH_ERROR_TEST",
                    "Path error with /home/user/sensitive/file.txt", 
                    "WARNING"
                )
                # Should not raise an exception - should use regex fallback
            except Exception as e:
                self.fail(f"log_security_event should handle OSError gracefully, but raised: {e}")
    
    def test_file_operation_path_resolution_failure_lines_191_193(self):
        """Test log_file_operation path resolution failure (lines 191-193)"""
        # Mock Path operations to raise ValueError during path resolution
        with patch('pathlib.Path.is_absolute', side_effect=ValueError("Path resolution failed")):
            # This should trigger the ValueError handling in lines 191-193
            try:
                log_file_operation(
                    "read", 
                    "/some/complex/path/that/fails/resolution.txt", 
                    True, 
                    size_bytes=1024
                )
                # Should not raise an exception - should use basename fallback
            except Exception as e:
                self.fail(f"log_file_operation should handle path resolution errors, but raised: {e}")
    
    def test_file_operation_path_os_error_lines_191_193(self):
        """Test log_file_operation path OSError (lines 191-193)"""
        # Mock Path operations to raise OSError during path processing
        with patch('pathlib.Path.is_relative_to', side_effect=OSError("File system access error")):
            # This should trigger the OSError handling in lines 191-193
            try:
                log_file_operation(
                    "write", 
                    "/inaccessible/path/file.txt", 
                    False, 
                    error="Write failed"
                )
                # Should not raise an exception - should use basename only
            except Exception as e:
                self.fail(f"log_file_operation should handle OSError gracefully, but raised: {e}")
    
    def test_path_name_extraction_error_lines_191_193(self):
        """Test fallback when even Path.name fails"""
        # Mock Path.name to also raise an exception
        with patch('pathlib.Path.is_absolute', side_effect=ValueError("Path error")):
            with patch('pathlib.Path.name', new_callable=lambda: property(lambda x: (_ for _ in ()).throw(Exception("Name extraction failed")))):
                # This should trigger both the main exception and the fallback exception
                try:
                    log_file_operation("test", "/problematic/path", True)
                    # Should still not crash the application
                except Exception as e:
                    self.fail(f"Should handle all path operation failures, but raised: {e}")
    
    def test_complex_path_scenarios(self):
        """Test various complex path scenarios that might trigger edge cases"""
        # Test with various problematic paths
        problematic_paths = [
            "",  # Empty path
            "/",  # Root path  
            "relative/path",  # Relative path
            "/path/with\x00null",  # Path with null character
            "/very/long/" + "a" * 1000 + "/path",  # Very long path
        ]
        
        for path in problematic_paths:
            # Mock path operations to fail in various ways
            with patch('pathlib.Path.is_absolute', side_effect=ValueError("Path operation failed")):
                try:
                    log_security_event("PATH_TEST", f"Testing path {path}", "INFO")
                    log_file_operation("test", path, True)
                    # All should handle gracefully
                except Exception as e:
                    self.fail(f"Should handle problematic path '{path}' gracefully, but raised: {e}")
    
    def test_regex_fallback_scenarios(self):
        """Test scenarios where regex fallback is used"""
        # Force path operations to fail so regex fallback is used
        with patch('pathlib.Path.is_absolute', side_effect=ValueError("Always fail")):
            with patch('pathlib.Path.is_relative_to', side_effect=OSError("Always fail")):
                # Test that regex fallback works for path redaction
                test_cases = [
                    "Error accessing /home/user/file.txt",
                    "Multiple paths: /path1 and /path2/file",
                    "Complex: /very/deep/path/structure/file.log failed",
                ]
                
                for details in test_cases:
                    try:
                        log_security_event("REGEX_TEST", details, "ERROR")
                        # Should use regex redaction as fallback
                    except Exception as e:
                        self.fail(f"Regex fallback should work for '{details}', but raised: {e}")


if __name__ == '__main__':
    unittest.main()