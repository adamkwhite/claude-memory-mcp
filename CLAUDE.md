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
- ✅ Fixed return type hint for add_conversation method
- ✅ Reduced cognitive complexity in search_conversations method
- ✅ Excluded archive/ and scripts/ folders from SonarQube analysis
- ✅ Added proper file formatting (newlines at end of files)

**SonarQube Configuration:**
- Instance: http://44.206.255.230:9000/
- Project Key: Claude-MCP
- Exclusions: `**/*test*/**,**/__pycache__/**,htmlcov/**,archive/**,scripts/**`

Current test coverage: **91.46%**

### Environment Setup

```bash
# Use Python 3.11 for this project
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest pytest-cov pytest-asyncio
```

## Git Workflow

**Important:** This repository has automated SonarQube badge updates that require special git workflow:

```bash
# Recommended workflow for commits
git pull                    # Always pull first (badges may have updated)
git add <files>
git commit -m "message"
git pull                    # Pull again before push (in case badges updated during commit)
git push
```

**Why this is needed:**
- GitHub Actions automatically updates `.badges/*.svg` files after each push
- SonarQube analysis runs and commits updated metrics badges
- Without pulling first, pushes will be rejected with "fetch first" errors
- This is normal behavior and indicates SonarQube improvements are working

## Project Management

**Task Tracking:** All todos and project tasks are maintained in `todos.md` for persistence across Claude Code sessions. This includes pending improvements, completed work, and priority classifications.