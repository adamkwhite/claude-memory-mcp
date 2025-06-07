# Claude Memory MCP - Local Development Notes

## Python Version Management

This project uses **Python 3.11** to match the CI environment, but the local system defaults to Python 3.8.10.

### Available Python Versions
- `python3` → Python 3.8.10 (system default)
- `python3.11` → Python 3.11.12 (preferred for this project)

### Recommended Commands

Always use `python3.11` explicitly for consistency with CI:

```bash
# Run tests
python3.11 -m pytest tests/test_100_percent_coverage.py --cov=src --cov-report=xml

# Install dependencies 
python3.11 -m pip install -r requirements.txt

# Run server
python3.11 src/server_fastmcp.py

# Create virtual environment with Python 3.11
python3.11 -m venv .venv
source .venv/bin/activate
```

### SonarQube Quality Gate

Recent fixes applied to resolve SonarQube issues:
- ✅ Replaced bare except clauses with specific exception types
- ✅ Removed unused import statements
- ✅ Extracted magic numbers to named constants
- ✅ Broke down complex methods (generate_weekly_summary)
- ✅ Added path validation for security
- ✅ Fixed README badge URLs to point to correct SonarQube instance

Current test coverage: **91.46%**

### Environment Setup

```bash
# Use Python 3.11 for this project
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest pytest-cov pytest-asyncio
```