"""Logging configuration for Claude Memory MCP system"""

import json
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
    get_default_log_file = None  # type: ignore[assignment]

# Control character removal pattern for log injection prevention
CONTROL_CHAR_PATTERN = r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]"


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging output.

    Outputs newline-delimited JSON (NDJSON) with standard fields:
    - timestamp: ISO 8601 formatted timestamp
    - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - logger: Logger name
    - function: Function name where log was called
    - line: Line number where log was called
    - message: Log message
    - context: Optional structured context data (if present in record.context)

    Example output:
    {"timestamp": "2025-01-15T10:30:45.123Z", "level": "INFO", "logger": "claude_memory_mcp",
     "function": "add_conversation", "line": 145, "message": "Added conversation successfully",
     "context": {"conversation_id": "abc123", "topics": ["python", "mcp"]}}
    """

    def format(self, record):
        """
        Format a log record as a JSON object.

        Args:
            record: LogRecord instance to format

        Returns:
            str: JSON-formatted log message (single line)
        """
        # Build standard log data structure
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt or "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add context if present in the log record
        if hasattr(record, "context"):
            log_data["context"] = record.context

        # Serialize to JSON with error handling
        try:
            return json.dumps(log_data)
        except (TypeError, ValueError) as e:
            # Fallback for non-serializable objects
            # Convert context to string representation if serialization fails
            if "context" in log_data:
                log_data["context"] = str(log_data["context"])
            try:
                return json.dumps(log_data)
            except Exception:
                # Ultimate fallback: return basic error message
                return json.dumps(
                    {
                        "timestamp": self.formatTime(
                            record, self.datefmt or "%Y-%m-%dT%H:%M:%S"
                        ),
                        "level": "ERROR",
                        "logger": "logging_config",
                        "message": f"Failed to serialize log record: {str(e)}",
                    }
                )


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        if hasattr(record, "levelname"):
            color = self.COLORS.get(record.levelname, "")
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def _get_log_format() -> str:
    """
    Get the log format from environment variable.

    Reads CLAUDE_MCP_LOG_FORMAT environment variable and validates the value.
    Valid values are 'json' or 'text'. Defaults to 'text' for backward compatibility.

    Returns:
        str: Log format ('json' or 'text')

    Environment Variables:
        CLAUDE_MCP_LOG_FORMAT: Log output format (json|text). Default: text
    """
    log_format = os.getenv("CLAUDE_MCP_LOG_FORMAT", "text").lower()

    # Validate format value
    valid_formats = ["json", "text"]
    if log_format not in valid_formats:
        # Log warning for invalid value and default to text
        logger = logging.getLogger("claude_memory_mcp")
        logger.warning(
            f"Invalid CLAUDE_MCP_LOG_FORMAT value: '{log_format}'. "
            f"Valid values are: {', '.join(valid_formats)}. Defaulting to 'text'."
        )
        return "text"

    return log_format


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5,
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

    Environment Variables:
        CLAUDE_MCP_LOG_FORMAT: Log format (json|text). Default: text
    """
    # Get logger
    logger = logging.getLogger("claude_memory_mcp")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers = []

    # Determine log format from environment variable
    log_format = _get_log_format()

    # Create formatters based on log format
    file_formatter: logging.Formatter
    console_formatter: logging.Formatter

    if log_format == "json":
        # Use JSON formatter for both console and file
        file_formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S")
        console_formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S")
    else:
        # Use text formatters (default)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_formatter = ColoredFormatter(
            "%(asctime)s | %(levelname)-8s | %(funcName)s() | %(message)s",
            datefmt="%H:%M:%S",
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
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "claude_memory_mcp") -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_function_call(func_name: str, **kwargs):
    """Log a function call with parameters and structured context"""
    try:
        logger = get_logger()
        # Only perform expensive parameter formatting if debug logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            # Create structured context for JSON logging
            context = {"type": "function_call", "function": func_name, "params": kwargs}
            params = ", ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
            logger.debug(f"Calling {func_name}({params})", extra={"context": context})
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


def log_performance(func_name: str, duration: float, **metrics):
    """Log performance metrics with structured context"""
    try:
        logger = get_logger()
        # Create structured context for JSON logging
        context = {"type": "performance", "duration_seconds": duration, **metrics}
        metric_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
        logger.info(
            f"Performance: {func_name} completed in {duration:.3f}s | {metric_str}",
            extra={"context": context},
        )
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


def log_security_event(event_type: str, details: str, severity: str = "WARNING"):
    """Log security-related events with structured context"""
    try:
        import re
        from pathlib import Path

        logger = get_logger("claude_memory_mcp.security")
        level = getattr(logging, severity.upper())

        # Sanitize event_type and details to prevent log injection
        safe_event_type = re.sub(CONTROL_CHAR_PATTERN, "", str(event_type))
        safe_details = re.sub(CONTROL_CHAR_PATTERN, "", str(details))

        # For path-related events, use relative paths to avoid information disclosure
        if "path" in safe_details.lower():
            try:
                # Try to make paths relative to home directory
                home = Path.home()
                safe_details = re.sub(
                    r"/[^\s]+",
                    lambda m: (
                        str(Path(m.group()).relative_to(home))
                        if Path(m.group()).is_absolute()
                        and Path(m.group()).is_relative_to(home)
                        else "<redacted_path>"
                    ),
                    safe_details,
                )
            except (ValueError, OSError):
                # If path operations fail, just redact the paths
                safe_details = re.sub(r"/[^\s]+", "<redacted_path>", safe_details)

        # Create structured context for JSON logging (with sanitized values)
        context = {
            "type": "security",
            "event_type": safe_event_type,
            "severity": severity,
            "details": safe_details,
        }

        logger.log(
            level,
            f"Security Event: {safe_event_type} | {safe_details}",
            extra={"context": context},
        )
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


def log_validation_failure(field: str, value: str, reason: str):
    """Log input validation failures with structured context"""
    try:
        import re

        logger = get_logger("claude_memory_mcp.validation")
        # Comprehensive sanitization to prevent log injection
        safe_value = str(value)[:100]
        # Remove all control characters except safe whitespace
        safe_value = re.sub(CONTROL_CHAR_PATTERN, "", safe_value)
        # Escape remaining newlines and carriage returns for visibility
        safe_value = safe_value.replace("\n", "\\n").replace("\r", "\\r")
        # Sanitize field and reason as well
        safe_field = re.sub(CONTROL_CHAR_PATTERN, "", str(field))
        safe_reason = re.sub(CONTROL_CHAR_PATTERN, "", str(reason))

        # Create structured context for JSON logging (with sanitized values)
        context = {
            "type": "validation",
            "field": safe_field,
            "value": safe_value,
            "reason": safe_reason,
        }

        logger.warning(
            f"Validation failed: {safe_field}='{safe_value}' | Reason: {safe_reason}",
            extra={"context": context},
        )
    except Exception:
        # Fail silently to prevent logging from crashing the application
        pass


def log_file_operation(operation: str, file_path: str, success: bool, **details):
    """Log file operations with structured context"""
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
            safe_k = re.sub(CONTROL_CHAR_PATTERN, "", str(k))
            safe_v = re.sub(CONTROL_CHAR_PATTERN, "", str(v))
            safe_details[safe_k] = safe_v

        # Create structured context for JSON logging (with sanitized values)
        context = {
            "type": "file_operation",
            "operation": operation,
            "path": safe_file_path,
            "success": success,
            **safe_details,
        }

        detail_str = ", ".join(f"{k}={v}" for k, v in safe_details.items())
        logger.info(
            f"File {operation}: {safe_file_path} | {status} | {detail_str}",
            extra={"context": context},
        )
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
        if get_default_log_file is not None:
            # Use path_utils for dynamic path resolution
            log_file = str(get_default_log_file())
        elif os.getenv("HOME"):
            # Fallback to manual construction
            log_file = os.path.join(
                os.getenv("HOME"), ".claude-memory", "logs", "claude-mcp.log"
            )

    # Disable console output for MCP server mode to prevent JSON-RPC interference
    console_output = os.getenv("CLAUDE_MCP_CONSOLE_OUTPUT", "false").lower() == "true"

    # Set up logging
    return setup_logging(
        log_level=log_level, log_file=log_file, console_output=console_output
    )
