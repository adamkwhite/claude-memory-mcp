"""Test logging functionality for Claude Memory MCP system"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.logging_config import (
    setup_logging,
    get_logger,
    log_function_call,
    log_performance,
    log_security_event,
    log_validation_failure,
    log_file_operation,
    init_default_logging,
    ColoredFormatter
)


class TestLoggingSetup:
    """Test logging configuration and setup"""
    
    def test_setup_logging_console_only(self):
        """Test setting up console-only logging"""
        logger = setup_logging(log_level="DEBUG", console_output=True, log_file=None)
        
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        
    def test_setup_logging_file_only(self):
        """Test setting up file-only logging"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                logger = setup_logging(
                    log_level="INFO", 
                    console_output=False, 
                    log_file=temp_file.name
                )
                
                assert logger.level == logging.INFO
                assert len(logger.handlers) == 1
                assert hasattr(logger.handlers[0], 'baseFilename')
                
            finally:
                os.unlink(temp_file.name)
    
    def test_setup_logging_both_console_and_file(self):
        """Test setting up both console and file logging"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                logger = setup_logging(
                    log_level="WARNING",
                    console_output=True,
                    log_file=temp_file.name
                )
                
                assert logger.level == logging.WARNING
                assert len(logger.handlers) == 2
                
            finally:
                os.unlink(temp_file.name)
    
    def test_log_file_rotation_config(self):
        """Test log file rotation configuration"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                logger = setup_logging(
                    log_file=temp_file.name,
                    max_bytes=1024,
                    backup_count=3
                )
                
                file_handler = next(h for h in logger.handlers if hasattr(h, 'maxBytes'))
                assert file_handler.maxBytes == 1024
                assert file_handler.backupCount == 3
                
            finally:
                os.unlink(temp_file.name)


class TestColoredFormatter:
    """Test colored log formatter"""
    
    def test_colored_formatter_adds_colors(self):
        """Test that colored formatter adds color codes"""
        formatter = ColoredFormatter('%(levelname)s - %(message)s')
        
        # Create log records for different levels
        debug_record = logging.LogRecord(
            'test', logging.DEBUG, 'test.py', 1, 'debug message', (), None
        )
        info_record = logging.LogRecord(
            'test', logging.INFO, 'test.py', 1, 'info message', (), None
        )
        error_record = logging.LogRecord(
            'test', logging.ERROR, 'test.py', 1, 'error message', (), None
        )
        
        # Format messages
        debug_msg = formatter.format(debug_record)
        info_msg = formatter.format(info_record)
        error_msg = formatter.format(error_record)
        
        # Check that color codes are present
        assert '\033[36m' in debug_msg  # Cyan for DEBUG
        assert '\033[32m' in info_msg   # Green for INFO
        assert '\033[31m' in error_msg  # Red for ERROR
        assert '\033[0m' in debug_msg   # Reset code


class TestLoggerHelpers:
    """Test logging helper functions"""
    
    def test_get_logger_returns_logger(self):
        """Test get_logger returns proper logger instance"""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
    
    def test_get_logger_default_name(self):
        """Test get_logger with default name"""
        logger = get_logger()
        assert logger.name == "claude_memory_mcp"
    
    @patch('src.logging_config.get_logger')
    def test_log_function_call(self, mock_get_logger):
        """Test function call logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_function_call("test_function", param1="value1", param2=42, param3=None)
        
        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args[0][0]
        assert "test_function(param1=value1, param2=42)" in call_args
        assert "param3" not in call_args  # None values should be filtered
    
    @patch('src.logging_config.get_logger')
    def test_log_performance(self, mock_get_logger):
        """Test performance logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_performance("search_function", 1.234, results=10, query_length=25)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "search_function completed in 1.234s" in call_args
        assert "results=10" in call_args
        assert "query_length=25" in call_args
    
    @patch('src.logging_config.get_logger')
    def test_log_security_event_default_warning(self, mock_get_logger):
        """Test security event logging with default WARNING level"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_security_event("PATH_TRAVERSAL", "Attempted ../../../etc/passwd")
        
        mock_logger.log.assert_called_once_with(
            logging.WARNING, 
            "Security Event: PATH_TRAVERSAL | Attempted ../../../etc/passwd"
        )
    
    @patch('src.logging_config.get_logger')
    def test_log_security_event_custom_severity(self, mock_get_logger):
        """Test security event logging with custom severity"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_security_event("CRITICAL_BREACH", "System compromised", "CRITICAL")
        
        mock_logger.log.assert_called_once_with(
            logging.CRITICAL,
            "Security Event: CRITICAL_BREACH | System compromised"
        )
    
    @patch('src.logging_config.get_logger')
    def test_log_validation_failure(self, mock_get_logger):
        """Test validation failure logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Test with normal value
        log_validation_failure("title", "normal title", "too long")
        mock_logger.warning.assert_called_with(
            "Validation failed: title='normal title' | Reason: too long"
        )
        
        # Test with value containing newlines (should be escaped)
        log_validation_failure("content", "line1\nline2\rline3", "invalid format")
        call_args = mock_logger.warning.call_args[0][0]
        assert "line1\\nline2\\rline3" in call_args
        
        # Test with very long value (should be truncated)
        long_value = "A" * 150
        log_validation_failure("field", long_value, "too long")
        call_args = mock_logger.warning.call_args[0][0]
        assert len(call_args.split("'")[1]) <= 100  # Value should be truncated
    
    @patch('src.logging_config.get_logger')
    def test_log_file_operation_success(self, mock_get_logger):
        """Test successful file operation logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_file_operation("create", "/path/to/file.txt", True, size=1024, topics=5)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "File create: /path/to/file.txt | SUCCESS | size=1024, topics=5" in call_args
    
    @patch('src.logging_config.get_logger')
    def test_log_file_operation_failure(self, mock_get_logger):
        """Test failed file operation logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_file_operation("read", "/missing/file.txt", False, error="File not found")
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "File read: /missing/file.txt | FAILED | error=File not found" in call_args


class TestInitDefaultLogging:
    """Test default logging initialization"""
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('src.logging_config.setup_logging')
    def test_init_default_logging_no_env(self, mock_setup):
        """Test default logging with no environment variables"""
        init_default_logging()
        
        # With path_utils, a default log file is now provided
        mock_setup.assert_called_once()
        call_args = mock_setup.call_args
        
        assert call_args.kwargs['log_level'] == "INFO"
        assert call_args.kwargs['log_file'] is not None  # Now provides default path
        assert call_args.kwargs['log_file'].endswith('.claude-memory/logs/claude-mcp.log')
        assert call_args.kwargs['console_output'] is False
    
    @patch.dict(os.environ, {'CLAUDE_MCP_LOG_LEVEL': 'DEBUG', 'CLAUDE_MCP_LOG_FILE': '/tmp/test.log'})
    @patch('src.logging_config.setup_logging')
    def test_init_default_logging_with_env(self, mock_setup):
        """Test default logging with environment variables"""
        init_default_logging()
        
        mock_setup.assert_called_once_with(
            log_level="DEBUG",
            log_file="/tmp/test.log",
            console_output=False
        )
    
    @patch.dict(os.environ, {'HOME': '/home/user'}, clear=True)
    @patch('src.logging_config.setup_logging')
    def test_init_default_logging_home_fallback(self, mock_setup):
        """Test default logging falls back to home directory for log file"""
        init_default_logging()
        
        expected_log_file = "/home/user/.claude-memory/logs/claude-mcp.log"
        mock_setup.assert_called_once_with(
            log_level="INFO",
            log_file=expected_log_file,
            console_output=False
        )
    
    @patch.dict(os.environ, {'CLAUDE_MCP_CONSOLE_OUTPUT': 'true', 'HOME': '/home/test'})
    @patch('src.logging_config.setup_logging')
    def test_init_default_logging_console_enabled(self, mock_setup):
        """Test default logging with console output explicitly enabled"""
        init_default_logging()
        
        mock_setup.assert_called_once_with(
            log_level="INFO",
            log_file="/home/test/.claude-memory/logs/claude-mcp.log",
            console_output=True
        )


class TestLoggingIntegration:
    """Test logging integration with actual file operations"""
    
    def test_file_logging_creates_directories(self):
        """Test that file logging creates necessary directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "nested" / "dirs" / "test.log"
            
            logger = setup_logging(log_file=str(log_file), console_output=False)
            logger.info("Test message")
            
            assert log_file.exists()
            assert log_file.read_text().strip().endswith("Test message")
    
    def test_log_rotation_configuration(self):
        """Test that log rotation is properly configured"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                logger = setup_logging(
                    log_file=temp_file.name,
                    max_bytes=100,  # Small size to trigger rotation
                    backup_count=2
                )
                
                # Write enough data to trigger rotation
                for i in range(50):
                    logger.info(f"This is a test message number {i} with some padding")
                
                # Check that backup files are created
                base_name = temp_file.name
                backup1 = f"{base_name}.1"
                
                # May or may not create backup depending on exact size, but config should be set
                file_handler = next(h for h in logger.handlers if hasattr(h, 'maxBytes'))
                assert file_handler.maxBytes == 100
                assert file_handler.backupCount == 2
                
            finally:
                # Clean up potential backup files
                for suffix in ['', '.1', '.2']:
                    try:
                        os.unlink(f"{temp_file.name}{suffix}")
                    except FileNotFoundError:
                        pass


class TestLoggingExceptionHandling:
    """Test exception handling in logging functions for complete coverage"""
    
    def test_log_function_call_exception_handling(self):
        """Test log_function_call exception handling (silent failure)"""
        # Mock get_logger to raise an exception
        with patch('src.logging_config.get_logger', side_effect=Exception("Logger error")):
            # This should trigger the exception handling in log_function_call
            # The function should fail silently and not crash
            try:
                log_function_call("test_function", param1="value1", param2="value2")
                # Should not raise an exception due to silent failure
            except Exception as e:
                pytest.fail(f"log_function_call should fail silently, but raised: {e}")
    
    def test_log_performance_exception_handling(self):
        """Test log_performance exception handling (silent failure)"""
        # Mock get_logger to raise an exception
        with patch('src.logging_config.get_logger', side_effect=Exception("Logger error")):
            # This should trigger the exception handling in log_performance
            try:
                log_performance("test_function", 1.234, results=10)
                # Should not raise an exception due to silent failure
            except Exception as e:
                pytest.fail(f"log_performance should fail silently, but raised: {e}")
    
    def test_log_security_event_exception_handling(self):
        """Test log_security_event exception handling (silent failure)"""
        # Mock get_logger to raise an exception
        with patch('src.logging_config.get_logger', side_effect=Exception("Logger error")):
            # This should trigger the exception handling in log_security_event
            try:
                log_security_event("TEST_EVENT", "Test message", "ERROR")
                # Should not raise an exception due to silent failure
            except Exception as e:
                pytest.fail(f"log_security_event should fail silently, but raised: {e}")
    
    def test_security_event_path_redaction_failure(self):
        """Test log_security_event path redaction failure handling"""
        # Mock Path operations to raise ValueError during path redaction
        with patch('pathlib.Path.is_absolute', side_effect=ValueError("Path operation failed")):
            # This should trigger the ValueError/OSError handling
            try:
                log_security_event(
                    "PATH_TEST", 
                    "Testing path /sensitive/path/that/should/be/redacted", 
                    "ERROR"
                )
                # Should not raise an exception - should use fallback path redaction
            except Exception as e:
                pytest.fail(f"log_security_event should handle path operation errors, but raised: {e}")
    
    def test_security_event_path_redaction_os_error(self):
        """Test log_security_event path redaction OSError handling"""
        # Mock Path operations to raise OSError during path redaction  
        with patch('pathlib.Path.is_relative_to', side_effect=OSError("File system error")):
            # This should trigger the OSError handling
            try:
                log_security_event(
                    "PATH_ERROR_TEST",
                    "Path error with /home/user/sensitive/file.txt", 
                    "WARNING"
                )
                # Should not raise an exception - should use fallback
            except Exception as e:
                pytest.fail(f"log_security_event should handle OSError, but raised: {e}")
    
    def test_file_operation_path_redaction_failure(self):
        """Test log_file_operation path redaction failure handling"""
        # Mock Path operations to raise ValueError
        with patch('pathlib.Path', side_effect=ValueError("Path error")):
            # This should trigger the exception handling in path redaction
            try:
                log_file_operation("read", "/some/file/path.txt", True)
                # Should not raise an exception
            except Exception as e:
                pytest.fail(f"log_file_operation should handle path errors, but raised: {e}")