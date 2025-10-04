# Implementation Tasks: Structured JSON Logging

## Relevant Files

- `src/logging_config.py` - Main logging configuration file; add JSONFormatter class and update setup_logging()
- `tests/test_json_logging.py` - New test file for JSON logging functionality
- `tests/test_logging_config.py` - Existing logging tests to update for JSON format support
- `README.md` - Add documentation for CLAUDE_MCP_LOG_FORMAT environment variable
- `docs/json-logging.md` - New documentation file with JSON schema and examples

## Tasks

- [x] 1.0 Implement JSONFormatter class and environment variable configuration
  - [x] 1.1 Create `JSONFormatter` class extending `logging.Formatter` in `src/logging_config.py`
  - [x] 1.2 Implement `format()` method to return newline-delimited JSON with standard fields (timestamp, level, logger, function, line, message)
  - [x] 1.3 Add support for optional `context` field via `record.context` attribute
  - [x] 1.4 Add try/except block for JSON serialization errors with fallback to string representation
  - [x] 1.5 Add `_get_log_format()` helper function to read `CLAUDE_MCP_LOG_FORMAT` environment variable (default: "text")
  - [x] 1.6 Add validation logic for environment variable (json/text), log warning for invalid values
  - [x] 1.7 Update `setup_logging()` function to select formatter based on environment variable
  - [x] 1.8 Ensure both console and file handlers use the same format (JSON or text)
  - [x] 1.9 Add inline documentation for JSONFormatter class and environment variable usage

- [ ] 2.0 Update specialized logging functions with structured context
  - [ ] 2.1 Update `log_performance()` (line 121-129) to include structured context: `{"type": "performance", "duration_seconds": duration, **metrics}`
  - [ ] 2.2 Update `log_security_event()` (line 132-161) to include structured context: `{"type": "security", "event_type": event_type, "severity": severity, "details": details}`
  - [ ] 2.3 Update `log_validation_failure()` (line 164-181) to include structured context: `{"type": "validation", "field": field, "value": value, "reason": reason}`
  - [ ] 2.4 Update `log_file_operation()` (line 184-213) to include structured context: `{"type": "file_operation", "operation": operation, "path": file_path, "success": success, **details}`
  - [ ] 2.5 Update `log_function_call()` (line 108-118) to include structured context: `{"type": "function_call", "function": func_name, "params": kwargs}`
  - [ ] 2.6 Ensure all sanitization and redaction logic still works with JSON context fields
  - [ ] 2.7 Test that text format still displays readable messages with context

- [ ] 3.0 Create comprehensive test suite for JSON logging
  - [ ] 3.1 Create `tests/test_json_logging.py` file with pytest fixtures for JSON and text loggers
  - [ ] 3.2 Add test for JSONFormatter basic functionality (test_json_formatter_basic_fields)
  - [ ] 3.3 Add test for all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) produce valid JSON
  - [ ] 3.4 Add test for JSON parsing with `json.loads()` to validate structure
  - [ ] 3.5 Add test for context field serialization (test_json_formatter_with_context)
  - [ ] 3.6 Add test for non-serializable objects (should fallback to string representation)
  - [ ] 3.7 Add test for environment variable handling (json/text/invalid values)
  - [ ] 3.8 Add integration test for `log_performance()` with JSON format
  - [ ] 3.9 Add integration test for `log_security_event()` with JSON format and path redaction
  - [ ] 3.10 Add integration test for `log_validation_failure()` with JSON format and sanitization
  - [ ] 3.11 Add integration test for `log_file_operation()` with JSON format
  - [ ] 3.12 Add integration test for `log_function_call()` with JSON format
  - [ ] 3.13 Add performance benchmark comparing JSON vs text formatting (ensure < 5% overhead)
  - [ ] 3.14 Run full test suite and ensure coverage remains ≥ 76%

- [ ] 4.0 Update documentation with JSON format examples
  - [ ] 4.1 Update `README.md` to add `CLAUDE_MCP_LOG_FORMAT` to environment variables section
  - [ ] 4.2 Add JSON logging examples to README showing sample JSON output
  - [ ] 4.3 Create `docs/json-logging.md` with comprehensive documentation
  - [ ] 4.4 Document JSON schema specification with all standard fields in `docs/json-logging.md`
  - [ ] 4.5 Add examples for each log type (performance, security, validation, file operation) in `docs/json-logging.md`
  - [ ] 4.6 Create migration guide section explaining how to switch from text to JSON format
  - [ ] 4.7 Add example configurations for log aggregation platforms (Datadog, ELK, CloudWatch)
  - [ ] 4.8 Add troubleshooting section for common JSON logging issues

- [ ] 5.0 Performance validation and backward compatibility verification
  - [ ] 5.1 Run performance benchmarks with 1000 log messages (JSON vs text)
  - [ ] 5.2 Verify performance overhead is < 5% as specified in requirements
  - [ ] 5.3 Test backward compatibility: ensure default behavior is text format with no environment variable
  - [ ] 5.4 Test that existing deployments work without changes (text format by default)
  - [ ] 5.5 Verify all security features work in JSON mode (sanitization, path redaction)
  - [ ] 5.6 Test file rotation compatibility with JSON format (newline-delimited)
  - [ ] 5.7 Run full pytest suite and verify all tests pass
  - [ ] 5.8 Run SonarQube analysis and ensure quality gates pass
  - [ ] 5.9 Manually test with real log aggregation tool (optional, if Datadog available)
  - [ ] 5.10 Validate all acceptance criteria from PRD are met
