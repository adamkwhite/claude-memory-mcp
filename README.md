## Code Quality
**Overall Scorecard**

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=alert_status)](https://sonarcloud.io/summary/overall?id=adamkwhite_claude-memory-mcp)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=bugs)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=bugs)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=coverage)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=coverage)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=reliability_rating)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=reliability_rating)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=security_rating)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=security_rating)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=sqale_rating)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=sqale_rating)

**Code Quality**

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=ncloc)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=ncloc)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=duplicated_lines_density)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=duplicated_lines_density)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=code_smells)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=code_smells)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=sqale_index)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=sqale_index)

**Security**

[![Security Hotspots](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=security_hotspots)](https://sonarcloud.io/project/security_hotspots?id=adamkwhite_claude-memory-mcp)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=adamkwhite_claude-memory-mcp&metric=vulnerabilities)](https://sonarcloud.io/component_measures?id=adamkwhite_claude-memory-mcp&metric=vulnerabilities)

# Claude Conversation Memory System

A Model Context Protocol (MCP) server that provides searchable local storage for Claude conversation history, enabling context retrieval during current sessions.

## Features

- 🔍 **Full-text search** across conversation history
- 🏷️ **Automatic topic extraction** and categorization  
- 📊 **Weekly summaries** with insights and patterns
- 🗃️ **Organized file storage** by date and topic
- ⚡ **Fast retrieval** with relevance scoring
- 🔌 **MCP integration** for seamless Claude Desktop access

## Quick Start

### Prerequisites

- Python 3.11+ (tested with 3.11.12)
- Ubuntu/WSL environment recommended
- Claude Desktop (for MCP integration)

### Installation

#### Option 1: Install with Claude Code (Recommended)

```bash
claude mcp add
```

When prompted, provide the following information:

1. **Server Name**: `claude-memory` (or your preferred name)
2. **Command**: `python3`
3. **Arguments**: `$HOME/Code/claude-memory-mcp/src/server_fastmcp.py`
4. **Working Directory**: `$HOME/Code/claude-memory-mcp`

**Important**: Adjust the path after `$HOME/` to match where you cloned this repository. The `$HOME` variable will automatically expand to your home directory (e.g., `/home/<user>`).

**Example**: If you cloned to `~/projects/claude-memory-mcp`:
- Arguments: `$HOME/projects/claude-memory-mcp/src/server_fastmcp.py`
- Working Directory: `$HOME/projects/claude-memory-mcp`

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

The system provides three main tools:

### `search_conversations(query, limit=5)`
Search through stored conversations by topic or content.

**Example:**
```python
search_conversations("terraform azure deployment")
search_conversations("python debugging", limit=10)
```

### `add_conversation(content, title, date)`
Add a new conversation to the memory system.

**Example:**
```python
add_conversation(
    content="Discussion about MCP server setup...",
    title="MCP Server Configuration", 
    date="2025-06-01T14:30:00Z"
)
```

### `generate_weekly_summary(week_offset=0)`
Generate insights and patterns from conversations.

**Example:**
```python
generate_weekly_summary()  # Current week
generate_weekly_summary(1)  # Last week
```

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
├── server_fastmcp.py           # Main MCP server
├── bulk_import_enhanced.py     # Conversation import tool
├── validate_system.py          # System validation
├── standalone_test.py          # Core functionality test
├── import_workflow.sh          # Automated import process
├── requirements.txt            # Python dependencies
├── IMPORT_GUIDE.md            # Detailed import instructions
└── README.md                  # This file
```

## Performance

Performance validated through automated benchmarks:

- **Search Speed**: 0.05s average (159 conversations)
- **Capacity**: Tested with 159 conversations (7.8MB)
- **Memory Usage**: 40MB peak during operations
- **Accuracy**: 80%+ search relevance
- **Write Performance**: 1-12MB/s throughput

*Last benchmarked: June 2025 | [Detailed Report](docs/PERFORMANCE_BENCHMARKS.md)*

**Note for Developers**: The development team uses performance benchmarks that create a `~/claude-memory-test` directory for isolated testing. **Normal MCP usage does NOT create this directory** - it only uses `~/claude-memory/`. If you see `~/claude-memory-test`, it was created by running development scripts and can be safely deleted.

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
**Last Updated**: June 2025  
**Version**: 1.0.0
