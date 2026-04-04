[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=adamkwhite_claude-memory-mcp)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=bugs)](https://sonarcloud.io/summary/new_code?id=adamkwhite_claude-memory-mcp)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=adamkwhite_claude-memory-mcp)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=adamkwhite_claude-memory-mcp)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=coverage)](https://sonarcloud.io/summary/new_code?id=adamkwhite_claude-memory-mcp)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=adamkwhite_claude-memory-mcp)

# Claude Memory MCP — Universal AI Conversation Memory

A Model Context Protocol (MCP) server that provides persistent, searchable conversation memory across multiple AI platforms. Store, search, and retrieve conversation history with sub-millisecond full-text search powered by SQLite FTS5.

## Features

- 🔍 **Sub-millisecond full-text search** via SQLite FTS5 with relevance ranking
- 🏷️ **Automatic topic extraction** — 574+ unique topics across 2,000+ associations
- 📊 **Weekly summaries** with insights and patterns
- 🗃️ **Organized file storage** by date and topic
- 🤖 **Multi-platform support** — Claude, ChatGPT, Cursor AI, and custom formats
- 🔌 **MCP integration** for Claude Desktop and Claude Code

## Quick Start

### Prerequisites

- Python 3.11+ (tested with 3.11.12)
- Ubuntu/WSL environment recommended
- Claude Desktop (for MCP integration)

### Installation

#### Option 1: Install with Claude Code (Recommended)

**Quick Install** - Copy and paste this into Claude Code:

```bash
claude mcp add --transport stdio claude-memory -- sh -c "cd $HOME/Code/claude-memory-mcp && python3 src/server_fastmcp.py"
```

**Important**: Replace `$HOME/Code/claude-memory-mcp` with the actual path where you cloned this repository.

**Examples for different locations:**

```bash
# If cloned to ~/Code/claude-memory-mcp (default)
claude mcp add --transport stdio claude-memory -- sh -c "cd $HOME/Code/claude-memory-mcp && python3 src/server_fastmcp.py"

# If cloned to ~/projects/claude-memory-mcp
claude mcp add --transport stdio claude-memory -- sh -c "cd $HOME/projects/claude-memory-mcp && python3 src/server_fastmcp.py"

# If cloned to ~/dev/claude-memory-mcp
claude mcp add --transport stdio claude-memory -- sh -c "cd $HOME/dev/claude-memory-mcp && python3 src/server_fastmcp.py"
```

**What this does:**
- `--transport stdio`: Uses standard input/output for local processes
- `claude-memory`: Server identifier name
- `--`: Separates Claude CLI flags from the server command
- `sh -c "cd ... && python3 ..."`: Changes to project directory before running server

This adds the MCP server to your Claude Desktop configuration automatically.

Documentation: https://code.claude.com/docs/en/mcp

#### Option 2: Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/claude-memory-mcp.git
   cd claude-memory-mcp
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

   This installs the package in editable mode along with all required dependencies:
   - `mcp[cli]>=1.9.2` - Model Context Protocol
   - `jsonschema>=4.0.0` - JSON schema validation
   - `aiofiles>=24.1.0` - Async file operations

4. **Test the system:**
   ```bash
   python3 tests/validate_system.py
   ```

### Basic Usage

#### Standalone Testing
```bash
# Test core functionality
python3 tests/standalone_test.py
```

#### MCP Server Mode
```bash
# Run as MCP server (from project root)
python3 src/server_fastmcp.py

# Or from src directory
cd src && python3 server_fastmcp.py
```

#### Bulk Import
```bash
# Import conversations from JSON export
python3 scripts/bulk_import_enhanced.py your_conversations.json
```

## MCP Tools

### `search_conversations(query, limit=5)`
Full-text search across all stored conversations with relevance ranking.

### `search_by_topic(topic, limit=10)`
Find conversations tagged with a specific topic.

### `add_conversation(content, title, date)`
Store a new conversation with automatic topic extraction and FTS indexing.

### `generate_weekly_summary(week_offset=0)`
Generate insights and patterns from recent conversations.

### `get_search_stats()`
View search engine statistics — index size, topic counts, and engine status.

## Architecture

```
~/claude-memory/
├── conversations/
│   ├── 2025/
│   │   └── 06-june/
│   │       └── 2025-06-01_topic-name.md
│   ├── index.json          # Search index
│   └── topics.json         # Topic frequency
└── summaries/
    └── weekly/
        └── week-2025-06-01.md
```

## Configuration

### Claude Desktop Integration

Add to your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "claude-memory": {
      "command": "python",
      "args": ["/path/to/claude-memory-mcp/server_fastmcp.py"]
    }
  }
}
```

### Storage Location

Default storage: `~/claude-memory/`

Override with environment variable:
```bash
export CLAUDE_MEMORY_PATH="/custom/path"
```

### Logging Configuration

#### Log Format

Switch between human-readable text logs (default) and structured JSON logs for production:

```bash
# JSON format (for production log aggregation)
export CLAUDE_MCP_LOG_FORMAT=json

# Text format (default, for development)
export CLAUDE_MCP_LOG_FORMAT=text
```

**JSON Log Example:**
```json
{
  "timestamp": "2025-01-15T10:30:45",
  "level": "INFO",
  "logger": "claude_memory_mcp",
  "function": "add_conversation",
  "line": 145,
  "message": "Added conversation successfully",
  "context": {
    "type": "performance",
    "duration_seconds": 0.045,
    "conversation_id": "conv_abc123"
  }
}
```

JSON logging is ideal for:
- Production deployments with log aggregation (Datadog, ELK, CloudWatch)
- Automated monitoring and alerting
- Structured log analysis and querying
- Performance tracking and debugging

See `docs/json-logging.md` for detailed JSON logging documentation.

## File Structure

```
claude-memory-mcp/
├── src/
│   ├── server_fastmcp.py       # Main MCP server
│   ├── conversation_memory.py  # Core memory engine + SQLite FTS5
│   ├── format_detector.py      # Auto-detect AI platform format
│   ├── validators.py           # Input validation
│   ├── logging_config.py       # Structured logging (text/JSON)
│   ├── importers/              # Platform-specific importers
│   │   ├── chatgpt_importer.py
│   │   ├── claude_importer.py
│   │   ├── cursor_importer.py
│   │   └── generic_importer.py
│   └── schemas/                # JSON schema validation
├── tests/                      # 435 tests, 98.68% coverage
├── data/                       # Consolidated app data
├── scripts/                    # Import and utility scripts
└── docs/                       # Documentation
```

## Performance

SQLite FTS5 full-text search, benchmarked against 347 indexed conversations:

- **Search Speed**: 0.2–0.5ms per query (4.4x faster than linear JSON scanning)
- **Topic Search**: 0.3–0.4ms across 574 unique topics
- **Write Speed**: ~33ms per conversation (includes indexing)
- **Capacity**: 371 conversations in production use over 10 months
- **Test Coverage**: 98.68% (435 tests) — 0 code smells, 0 security hotspots (SonarCloud verified)

*Last benchmarked: April 2026 | [Detailed Report](docs/PERFORMANCE_BENCHMARKS.md)*

**Note for Developers**: Performance benchmarks create a `~/claude-memory-test` directory for isolated testing. Normal MCP usage only uses `~/claude-memory/`. If you see `~/claude-memory-test`, it can be safely deleted.

## Search Examples

```python
# Technical topics
search_conversations("terraform azure")
search_conversations("mcp server setup")
search_conversations("python debugging")

# Project discussions  
search_conversations("interview preparation")
search_conversations("product management")
search_conversations("architecture decisions")

# Specific problems
search_conversations("dependency issues")
search_conversations("authentication error")
search_conversations("deployment configuration")
```

## Development

### Adding New Features

1. **Topic Extraction**: Modify `_extract_topics()` in `ConversationMemoryServer`
2. **Search Algorithm**: Enhance `search_conversations()` method
3. **Summary Generation**: Improve `generate_weekly_summary()` logic

### Testing

```bash
# Run validation suite
python3 tests/validate_system.py

# Test individual components
python3 tests/standalone_test.py

# Run full test suite with coverage
python3 -m pytest tests/ --ignore=tests/standalone_test.py --cov=src --cov-report=term

# Import test data
python3 scripts/bulk_import_enhanced.py test_data.json --dry-run
```

**Test Data Storage (Developers Only)**: If you run performance benchmarks or test data generators, they create a `~/claude-memory-test` directory to isolate test data from your production `~/claude-memory` directory. **This is only for development/testing** - normal MCP usage does not create this directory.

To clean up test data after running benchmarks:

```bash
rm -rf ~/claude-memory-test
```

Or using the Makefile cleanup target:

```bash
make clean-test-data
```

## Troubleshooting

### Common Issues

**MCP Import Errors:**
```bash
pip install mcp[cli]  # Include CLI extras
```

**Search Returns No Results:**
- Check conversation indexing: `ls ~/claude-memory/conversations/index.json`
- Verify file permissions
- Run validation: `python3 tests/validate_system.py`

**Weekly Summary Timezone Errors:**
- Ensure all datetime objects use consistent timezone handling
- Recent fix addresses timezone-aware vs naive comparison

### System Requirements

- **Python**: 3.11+ (tested with 3.11.12)
- **Disk Space**: ~10MB per 100 conversations
- **Memory**: <100MB RAM usage
- **OS**: Ubuntu/WSL recommended, macOS/Windows compatible

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk)
- Designed for [Claude Desktop](https://claude.ai/desktop) integration
- Inspired by the need for persistent conversation context

---

**Status**: Production ready ✅  
**Last Updated**: April 2026  
**Version**: 2.0.0
