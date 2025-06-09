"""Logging configuration for Claude Memory MCP system"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


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
    logger = get_logger()
    params = ", ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
    logger.debug(f"Calling {func_name}({params})")


def log_performance(func_name: str, duration: float, **metrics):
    """Log performance metrics"""
    logger = get_logger()
    metric_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
    logger.info(f"Performance: {func_name} completed in {duration:.3f}s | {metric_str}")


def log_security_event(event_type: str, details: str, severity: str = "WARNING"):
    """Log security-related events"""
    logger = get_logger("claude_memory_mcp.security")
    level = getattr(logging, severity.upper())
    logger.log(level, f"Security Event: {event_type} | {details}")


def log_validation_failure(field: str, value: str, reason: str):
    """Log input validation failures"""
    logger = get_logger("claude_memory_mcp.validation")
    # Sanitize potentially dangerous values for logging
    safe_value = str(value)[:100].replace('\n', '\\n').replace('\r', '\\r')
    logger.warning(f"Validation failed: {field}='{safe_value}' | Reason: {reason}")


def log_file_operation(operation: str, file_path: str, success: bool, **details):
    """Log file operations"""
    logger = get_logger("claude_memory_mcp.files")
    status = "SUCCESS" if success else "FAILED"
    detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
    logger.info(f"File {operation}: {file_path} | {status} | {detail_str}")


# Default logging setup for the application
def init_default_logging():
    """Initialize default logging configuration"""
    # Get log level from environment or default to INFO
    log_level = os.getenv("CLAUDE_MCP_LOG_LEVEL", "INFO")
    
    # Get log file path from environment
    log_file = os.getenv("CLAUDE_MCP_LOG_FILE")
    if not log_file and os.getenv("HOME"):
        log_file = os.path.join(os.getenv("HOME"), ".claude-memory", "logs", "claude-mcp.log")
    
    # Set up logging
    return setup_logging(
        log_level=log_level,
        log_file=log_file,
        console_output=True
    )