"""Logging configuration for Claude Memory MCP system"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

# Import path utilities for dynamic path resolution
try:
    from path_utils import get_default_log_file
except ImportError:
    # Fallback if path_utils is not available
    get_default_log_file = None

# Control character removal pattern for log injection prevention
CONTROL_CHAR_PATTERN = r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]'


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up comprehensive logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        console_output: Whether to output to console
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    # Get logger
    logger = logging.getLogger("claude_memory_mcp")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(funcName)s() | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "claude_memory_mcp") -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_function_call(func_name: str, **kwargs):
    """Log a function call with parameters"""
    try:
        logger = get_logger()
        # Only perform expensive parameter formatting if debug logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            params = ", ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
            logger.debug(f"Calling {func_name}({params})")
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


def log_performance(func_name: str, duration: float, **metrics):
    """Log performance metrics"""
    try:
        logger = get_logger()
        metric_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
        logger.info(f"Performance: {func_name} completed in {duration:.3f}s | {metric_str}")
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


def log_security_event(event_type: str, details: str, severity: str = "WARNING"):
    """Log security-related events"""
    try:
        import re
        from pathlib import Path
        logger = get_logger("claude_memory_mcp.security")
        level = getattr(logging, severity.upper())
        
        # Sanitize event_type and details to prevent log injection
        safe_event_type = re.sub(CONTROL_CHAR_PATTERN, '', str(event_type))
        safe_details = re.sub(CONTROL_CHAR_PATTERN, '', str(details))
        
        # For path-related events, use relative paths to avoid information disclosure
        if 'path' in safe_details.lower():
            try:
                # Try to make paths relative to home directory
                home = Path.home()
                safe_details = re.sub(
                    r'/[^\s]+',
                    lambda m: str(Path(m.group()).relative_to(home)) if Path(m.group()).is_absolute() and Path(m.group()).is_relative_to(home) else '<redacted_path>',
                    safe_details
                )
            except (ValueError, OSError):
                # If path operations fail, just redact the paths
                safe_details = re.sub(r'/[^\s]+', '<redacted_path>', safe_details)
        
        logger.log(level, f"Security Event: {safe_event_type} | {safe_details}")
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


def log_validation_failure(field: str, value: str, reason: str):
    """Log input validation failures"""
    try:
        import re
        logger = get_logger("claude_memory_mcp.validation")
        # Comprehensive sanitization to prevent log injection
        safe_value = str(value)[:100]
        # Remove all control characters except safe whitespace
        safe_value = re.sub(CONTROL_CHAR_PATTERN, '', safe_value)
        # Escape remaining newlines and carriage returns for visibility
        safe_value = safe_value.replace('\n', '\\n').replace('\r', '\\r')
        # Sanitize field and reason as well
        safe_field = re.sub(CONTROL_CHAR_PATTERN, '', str(field))
        safe_reason = re.sub(CONTROL_CHAR_PATTERN, '', str(reason))
        logger.warning(f"Validation failed: {safe_field}='{safe_value}' | Reason: {safe_reason}")
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


def log_file_operation(operation: str, file_path: str, success: bool, **details):
    """Log file operations"""
    try:
        import re
        from pathlib import Path
        logger = get_logger("claude_memory_mcp.files")
        status = "SUCCESS" if success else "FAILED"
        
        # Sanitize file path for logging (use relative path when possible)
        safe_file_path = str(file_path)
        try:
            home = Path.home()
            if Path(file_path).is_absolute() and Path(file_path).is_relative_to(home):
                safe_file_path = str(Path(file_path).relative_to(home))
        except (ValueError, OSError):
            # Use basename only if path operations fail
            safe_file_path = Path(file_path).name
        
        # Sanitize details
        safe_details = {}
        for k, v in details.items():
            safe_k = re.sub(CONTROL_CHAR_PATTERN, '', str(k))
            safe_v = re.sub(CONTROL_CHAR_PATTERN, '', str(v))
            safe_details[safe_k] = safe_v
        
        detail_str = ", ".join(f"{k}={v}" for k, v in safe_details.items())
        logger.info(f"File {operation}: {safe_file_path} | {status} | {detail_str}")
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


# Default logging setup for the application
def init_default_logging():
    """Initialize default logging configuration"""
    # Get log level from environment or default to INFO
    log_level = os.getenv("CLAUDE_MCP_LOG_LEVEL", "INFO")
    
    # Get log file path from environment or use default
    log_file = os.getenv("CLAUDE_MCP_LOG_FILE")
    if not log_file:
        if get_default_log_file:
            # Use path_utils for dynamic path resolution
            log_file = str(get_default_log_file())
        elif os.getenv("HOME"):
            # Fallback to manual construction
            log_file = os.path.join(os.getenv("HOME"), ".claude-memory", "logs", "claude-mcp.log")
    
    # Disable console output for MCP server mode to prevent JSON-RPC interference
    console_output = os.getenv("CLAUDE_MCP_CONSOLE_OUTPUT", "false").lower() == "true"
    
    # Set up logging
    return setup_logging(
        log_level=log_level,
        log_file=log_file,
        console_output=console_output
    )