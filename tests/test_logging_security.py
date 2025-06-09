"""Test security improvements for logging functions"""

import pytest
import logging
from unittest.mock import patch, MagicMock

from src.logging_config import (
    log_validation_failure,
    log_security_event,
    log_file_operation,
    log_function_call
)


class TestLoggingSecurity:
    """Test security enhancements in logging functions"""
    
    @patch('src.logging_config.get_logger')
    def test_log_injection_prevention_validation(self, mock_get_logger):
        """Test that log injection is prevented in validation logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Test with malicious input containing control characters
        malicious_value = "normal\x00\x01\x02\x1f\x7f\x9ftext"
        log_validation_failure("field", malicious_value, "test reason")
        
        # Verify that control characters were stripped
        call_args = mock_logger.warning.call_args[0][0]
        assert "\x00" not in call_args
        assert "\x01" not in call_args
        assert "\x1f" not in call_args
        assert "\x7f" not in call_args
        assert "\x9f" not in call_args
        assert "normaltext" in call_args
    
    @patch('src.logging_config.get_logger')
    def test_log_injection_prevention_security_events(self, mock_get_logger):
        """Test that log injection is prevented in security event logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Test with malicious input without path (to avoid path redaction)
        malicious_details = "attempt detected\x00\x1b[31mFAKE ERROR\x1b[0m"
        log_security_event("TEST_EVENT", malicious_details, "WARNING")
        
        # Verify that control characters were stripped
        call_args = mock_logger.log.call_args[0][1]
        assert "\x00" not in call_args
        assert "\x1b" not in call_args
        assert "FAKE ERROR" in call_args  # Text should remain
    
    @patch('src.logging_config.get_logger')
    @patch('pathlib.Path.home')
    def test_path_redaction_in_security_events(self, mock_home, mock_get_logger):
        """Test that absolute paths are redacted in security events"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_home.return_value = "/home/user"
        
        # Test with absolute path
        details_with_path = "Storage path outside home directory: /home/user/documents/secret.txt"
        log_security_event("PATH_VIOLATION", details_with_path)
        
        call_args = mock_logger.log.call_args[0][1]
        # Should contain relative path or redacted path
        assert "documents/secret.txt" in call_args or "redacted_path" in call_args
    
    @patch('src.logging_config.get_logger')
    @patch('pathlib.Path.home')
    def test_file_path_sanitization(self, mock_home, mock_get_logger):
        """Test that file paths are sanitized in file operation logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_home.return_value = "/home/user"
        
        # Test with absolute path
        log_file_operation("create", "/home/user/claude-memory/test.txt", True, size=100)
        
        call_args = mock_logger.info.call_args[0][0]
        # Should use relative path
        assert "claude-memory/test.txt" in call_args
        assert "/home/user" not in call_args
    
    @patch('src.logging_config.get_logger')
    def test_performance_conditional_debug_logging(self, mock_get_logger):
        """Test that debug logging is conditional for performance"""
        mock_logger = MagicMock()
        mock_logger.isEnabledFor.return_value = False  # Debug disabled
        mock_get_logger.return_value = mock_logger
        
        # Call function with debug logging
        log_function_call("test_function", param1="value1", param2="value2")
        
        # Should check if debug is enabled
        mock_logger.isEnabledFor.assert_called_once_with(logging.DEBUG)
        # Should not call debug if disabled
        mock_logger.debug.assert_not_called()
        
        # Test with debug enabled
        mock_logger.reset_mock()
        mock_logger.isEnabledFor.return_value = True
        
        log_function_call("test_function", param1="value1", param2="value2")
        
        # Should now call debug
        mock_logger.debug.assert_called_once()
    
    @patch('src.logging_config.get_logger')
    def test_error_handling_prevents_crashes(self, mock_get_logger):
        """Test that logging errors don't crash the application"""
        # Mock logger that raises exceptions
        mock_logger = MagicMock()
        mock_logger.warning.side_effect = Exception("Logging failed")
        mock_get_logger.return_value = mock_logger
        
        # Should not raise exception
        try:
            log_validation_failure("field", "value", "reason")
            # If we get here, the exception was caught
            assert True
        except Exception:
            pytest.fail("Logging function should not raise exceptions")
    
    @patch('src.logging_config.get_logger')
    def test_newline_carriage_return_escaping(self, mock_get_logger):
        """Test that newlines and carriage returns are properly escaped"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Test with newlines and carriage returns
        value_with_newlines = "line1\nline2\rline3"
        log_validation_failure("field", value_with_newlines, "test")
        
        call_args = mock_logger.warning.call_args[0][0]
        assert "line1\\nline2\\rline3" in call_args
        assert "\n" not in call_args.split("'")[1]  # No actual newlines in the value
        assert "\r" not in call_args.split("'")[1]  # No actual carriage returns
    
    @patch('src.logging_config.get_logger')
    def test_value_truncation(self, mock_get_logger):
        """Test that long values are properly truncated"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Test with very long value
        long_value = "A" * 200
        log_validation_failure("field", long_value, "test")
        
        call_args = mock_logger.warning.call_args[0][0]
        # Extract the value part between quotes
        logged_value = call_args.split("'")[1]
        assert len(logged_value) <= 100  # Should be truncated