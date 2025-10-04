# PRD: Structured JSON Logging

## Overview

Add optional structured JSON logging format to enable better integration with production observability platforms (Datadog, ELK, CloudWatch) while maintaining backward compatibility with existing human-readable text format.

## Problem Statement

**Current State:**
- Logging outputs human-readable formatted text suitable for local development
- Log format is not machine-parseable for automated analysis
- Difficult to query logs by specific fields (function name, error type, performance metrics)
- Integration with log aggregation platforms requires custom parsing logic
- Production observability limited to string-based searches

**Why This Matters:**
- Production deployments need machine-readable logs for automated monitoring and alerting
- Log aggregation platforms (Datadog, Splunk, ELK) work best with structured JSON
- Querying capabilities are limited with text-based logs
- Performance analysis requires parsing text logs manually
- Security event tracking is harder without structured fields

## Goals

### Primary Goals
1. Enable JSON-formatted logging for production observability
2. Maintain 100% backward compatibility with existing text format
3. Preserve all existing security features (sanitization, path redaction)
4. Support all existing specialized log functions with structured fields

### Secondary Goals
1. Improve logging structure with additional context fields
2. Simplify log parsing for automated analysis
3. Enable future enhancements (correlation IDs, distributed tracing)

## Success Criteria

- [ ] JSON formatter produces valid, parseable JSON for all log types
- [ ] Format switchable via `CLAUDE_MCP_LOG_FORMAT` environment variable
- [ ] All existing log functions work with JSON format
- [ ] Security features (sanitization, redaction) work in JSON mode
- [ ] Automated tests validate JSON structure and content
- [ ] Documentation updated with JSON format examples
- [ ] Zero breaking changes to existing deployments
- [ ] Performance overhead < 5% compared to text logging

## Requirements

### Functional Requirements

**FR-1: JSON Formatter Class**
- Create `JSONFormatter` class extending `logging.Formatter`
- Output valid JSON objects with consistent schema
- One JSON object per log line (newline-delimited JSON)
- Include standard fields: timestamp, level, logger, function, line, message
- Support additional context via `extra` parameter

**FR-2: Environment Variable Control**
- New environment variable: `CLAUDE_MCP_LOG_FORMAT` (values: `json`, `text`)
- Default to `text` for backward compatibility
- Apply format choice to both console and file handlers
- Validate environment variable value on startup

**FR-3: Structured Context Fields**
- All specialized log functions include structured context:
  - `log_function_call`: `{"type": "function_call", "params": {...}}`
  - `log_performance`: `{"type": "performance", "duration": 0.123, "metrics": {...}}`
  - `log_security_event`: `{"type": "security", "event_type": "...", "severity": "..."}`
  - `log_validation_failure`: `{"type": "validation", "field": "...", "reason": "..."}`
  - `log_file_operation`: `{"type": "file_operation", "operation": "...", "path": "...", "success": true}`

**FR-4: Security Feature Preservation**
- Sanitization functions work in JSON mode
- Path redaction applies to JSON context fields
- Log injection prevention for JSON values
- No sensitive data in JSON output

**FR-5: ColoredFormatter Enhancement (Opportunity to Improve)**
- Add context field display to text format where appropriate
- Maintain readability while showing relevant context
- Optional: Add indentation for multi-line messages in text mode

### Technical Requirements

**TR-1: Python Standard Library Only**
- Use only `json` module from standard library
- No external dependencies for JSON formatting
- Maintain compatibility with Python 3.11+

**TR-2: Performance**
- JSON serialization overhead < 5% compared to text formatting
- Lazy evaluation of context data (only serialize if logging enabled)
- Reuse JSON encoder instance to minimize allocations

**TR-3: Error Handling**
- JSON serialization errors must not crash logging
- Fall back to text representation for non-serializable objects
- Log serialization failures at WARNING level

**TR-4: File Rotation Compatibility**
- JSON format works with existing `RotatingFileHandler`
- Each log line is a complete JSON object (newline-delimited)
- No multi-line JSON objects that could break rotation

### Non-Functional Requirements

**NFR-1: Backward Compatibility**
- Existing deployments continue working without changes
- Text format remains the default
- No changes to function signatures or log function APIs

**NFR-2: Testability**
- Unit tests for JSONFormatter with various log levels
- Integration tests parsing JSON output
- Tests for all specialized log functions in JSON mode
- Performance benchmarks comparing JSON vs text

**NFR-3: Documentation**
- Environment variable documented in README
- JSON schema examples in documentation
- Migration guide for switching to JSON format
- Example log aggregation platform configurations

**NFR-4: Maintainability**
- Clear separation between JSON and text formatting logic
- Shared sanitization/security functions
- Comprehensive inline documentation

## User Stories

**US-1: Production Deployment**
As a DevOps engineer, I want to configure JSON logging via environment variable so that logs can be ingested by Datadog without custom parsing logic.

**US-2: Performance Analysis**
As a developer, I want performance metrics in structured JSON fields so that I can query slow operations using log aggregation tools.

**US-3: Security Monitoring**
As a security analyst, I want security events in structured JSON so that I can set up automated alerts for suspicious activities.

**US-4: Development Debugging**
As a developer, I want to keep using human-readable text logs locally so that debugging remains easy during development.

**US-5: Error Investigation**
As an on-call engineer, I want to query errors by function name and context fields so that I can quickly identify the root cause of production issues.

## Technical Specifications

### JSON Log Schema

**Standard Fields (Always Present):**
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "claude_memory_mcp",
  "function": "add_conversation",
  "line": 145,
  "message": "Added conversation successfully"
}
```

**With Context Fields:**
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "claude_memory_mcp",
  "function": "add_conversation",
  "line": 145,
  "message": "Added conversation successfully",
  "context": {
    "conversation_id": "conv_abc123",
    "topics": ["python", "mcp"],
    "file_path": "conversations/2025/01-january/python-tutorial.md"
  }
}
```

**Performance Log:**
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "claude_memory_mcp",
  "function": "search_conversations",
  "line": 212,
  "message": "Performance: search_conversations completed in 0.045s",
  "context": {
    "type": "performance",
    "duration_seconds": 0.045,
    "query": "python tutorial",
    "results_count": 15
  }
}
```

**Security Event:**
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "WARNING",
  "logger": "claude_memory_mcp.security",
  "function": "validate_path",
  "line": 78,
  "message": "Security Event: path_traversal_attempt",
  "context": {
    "type": "security",
    "event_type": "path_traversal_attempt",
    "severity": "WARNING",
    "details": "Blocked path: <redacted_path>"
  }
}
```

### Environment Variable Configuration

```bash
# JSON format (for production)
export CLAUDE_MCP_LOG_FORMAT=json

# Text format (default, for development)
export CLAUDE_MCP_LOG_FORMAT=text

# Invalid value defaults to text with warning
export CLAUDE_MCP_LOG_FORMAT=invalid
```

### Code Implementation Pattern

**JSONFormatter Class:**
```python
class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }

        # Add context if present
        if hasattr(record, 'context'):
            log_data['context'] = record.context

        try:
            return json.dumps(log_data)
        except (TypeError, ValueError) as e:
            # Fallback for non-serializable objects
            log_data['context'] = str(log_data.get('context', {}))
            return json.dumps(log_data)
```

**Updated setup_logging:**
```python
def setup_logging(...):
    # ... existing code ...

    # Determine log format from environment
    log_format = os.getenv("CLAUDE_MCP_LOG_FORMAT", "text").lower()

    if log_format == "json":
        console_formatter = JSONFormatter()
        file_formatter = JSONFormatter()
    else:
        console_formatter = ColoredFormatter(...)
        file_formatter = logging.Formatter(...)

    # ... rest of existing code ...
```

**Updated Specialized Log Functions:**
```python
def log_performance(func_name: str, duration: float, **metrics):
    try:
        logger = get_logger()
        context = {
            "type": "performance",
            "duration_seconds": duration,
            **metrics
        }
        logger.info(
            f"Performance: {func_name} completed in {duration:.3f}s",
            extra={"context": context}
        )
    except Exception:
        pass
```

## Dependencies

### Internal Dependencies
- `src/logging_config.py` - Primary file to modify
- All modules using logging functions (validation updates for context)

### External Dependencies
- None (uses Python standard library `json` module)

## Timeline

### Phase 1: Core Implementation (2-3 hours)
- Create `JSONFormatter` class
- Add environment variable handling
- Update `setup_logging` function
- Basic unit tests for JSON output

### Phase 2: Specialized Functions (2-3 hours)
- Update `log_performance` with structured context
- Update `log_security_event` with structured context
- Update `log_validation_failure` with structured context
- Update `log_file_operation` with structured context
- Update `log_function_call` with structured context

### Phase 3: Testing & Validation (2-3 hours)
- Comprehensive unit tests for all log types
- JSON parsing integration tests
- Security feature validation in JSON mode
- Performance benchmarking

### Phase 4: Documentation (1-2 hours)
- Update README with JSON logging examples
- Add JSON schema documentation
- Create migration guide
- Add example log aggregation configurations

**Total Estimated Time:** 7-11 hours

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| JSON serialization errors break logging | High | Implement try/catch with fallback to string representation |
| Performance degradation in high-traffic scenarios | Medium | Benchmark early; lazy evaluate context; reuse encoder |
| Security features don't work in JSON mode | High | Comprehensive tests for sanitization and redaction in JSON |
| Breaking changes for existing deployments | High | Default to text format; thorough backward compatibility testing |
| Non-serializable objects in context | Medium | Custom JSON encoder with fallback to repr() |

## Out of Scope

### Explicitly Not Included
- **Hybrid mode** (simultaneous JSON + text output) - can be added later if needed
- **Runtime format switching** - only startup configuration via environment variable
- **Custom JSON schemas per log type** - using consistent schema for all logs
- **Log aggregation platform integrations** - users configure platforms themselves
- **Correlation IDs** - tracked in separate issue #16 (depends on this work)
- **Async logging** - current synchronous logging is sufficient
- **Log sampling** - tracked in separate issue #15
- **Structured text format** (e.g., logfmt) - JSON only for now

### Future Enhancements
- Correlation ID support (issue #16)
- Log sampling for high-frequency operations (issue #15)
- Custom JSON encoders for application-specific types
- Structured context propagation through call chains
- OpenTelemetry integration

## Acceptance Criteria

### Functional Acceptance
- [ ] `CLAUDE_MCP_LOG_FORMAT=json` produces valid JSON output
- [ ] `CLAUDE_MCP_LOG_FORMAT=text` maintains current behavior (default)
- [ ] All specialized log functions include structured context in JSON mode
- [ ] Security sanitization works correctly in JSON output
- [ ] Path redaction functions correctly with JSON context fields
- [ ] JSON format works with file rotation
- [ ] Invalid format values default to text with warning logged

### Technical Acceptance
- [ ] JSON output parses correctly with `json.loads()`
- [ ] Schema matches documented specification
- [ ] No breaking changes to existing function signatures
- [ ] All existing tests pass without modification
- [ ] New tests added for JSON formatter (>95% coverage)
- [ ] Performance overhead < 5% vs text format

### Quality Acceptance
- [ ] Code review completed
- [ ] Documentation updated
- [ ] All tests passing (pytest)
- [ ] SonarQube quality gates pass
- [ ] No new security vulnerabilities introduced

## Related Work

- **Issue #52**: Implementation tracking for JSON logging feature - https://github.com/adamkwhite/claude-memory-mcp/issues/52
- **Issue #16**: Add correlation IDs (future enhancement building on this) - https://github.com/adamkwhite/claude-memory-mcp/issues/16
- **Issue #15**: Implement log sampling (complementary feature) - https://github.com/adamkwhite/claude-memory-mcp/issues/15

## References

- Current logging implementation: `src/logging_config.py:40-240`
- Python logging documentation: https://docs.python.org/3/library/logging.html
- JSON Lines format: https://jsonlines.org/
- Datadog log format: https://docs.datadoghq.com/logs/log_configuration/parsing/
