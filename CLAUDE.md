# Claude Memory MCP - Universal AI Memory System

## Project Overview

**Claude Memory MCP** is a universal conversation memory system that provides persistent storage and intelligent search across multiple AI platforms. Originally designed for Claude, it now supports ChatGPT, Cursor AI, and custom formats through an extensible architecture.

## Current Status (October 19, 2025)

**Branch**: `main`
**Recent Work**: Context Optimization - Disabled `migrate_to_sqlite` MCP tool (saves 573 tokens)
**Test Coverage**: 78% overall (435 tests passing)
**Code Quality**: 0 code smells, 0 security hotspots, CI/CD fully functional
**Async Compliance**: All async file I/O operations converted to aiofiles
**Context Efficiency**: Removed unnecessary MCP tools from default context

### Recent Major Implementations
- ✅ **Async File I/O Migration**: Converted all synchronous file operations to async using aiofiles
- ✅ **SonarCloud Quality Gates**: All code quality issues resolved, 80%+ coverage on new code
- ✅ **Universal Memory Framework**: Complete architecture for multi-platform support
- ✅ **ChatGPT Integration**: Production-ready with real export validation and jsonschema validation
- ✅ **SQLite FTS Search**: 4.4x performance improvement over linear search
- ✅ **Comprehensive Testing**: 435/435 tests passing with complete edge case coverage
- ✅ **CI/CD Pipeline**: GitHub Actions with SonarCloud integration fully operational

## Technology Stack

**Core Technologies:**
- **Python 3.11+**: Primary development language
- **FastMCP**: Model Context Protocol server implementation
- **aiofiles**: Async file I/O operations for proper async/await compliance
- **SQLite FTS5**: Full-text search with relevance scoring
- **JSON Schema**: Platform format validation with jsonschema library
- **pytest**: Comprehensive testing framework with 435 test cases

**AI Platform Support:**
- **ChatGPT**: Complete OpenAI export format support
- **Cursor AI**: Session-based development context imports
- **Claude**: Multiple variants (web, desktop, memory)
- **Generic**: Flexible parsing for custom formats

**Quality Assurance:**
- **SonarCloud**: Code quality analysis with public dashboard visibility
- **GitHub Actions**: CI/CD with quality gate enforcement
- **98.68% Test Coverage**: Industry-leading reliability standards

## Project Structure

**As of June 2025, the project uses a consolidated data/ directory structure:**

```
claude-memory-mcp/
├── data/                    # Consolidated application data
│   ├── conversations/       # Local conversation storage  
│   ├── summaries/          # Weekly summary storage
│   └── config/             # Project configuration files
├── pyproject.toml          # Symlink to data/config/pyproject.toml
├── pytest.ini             # Symlink to data/config/pytest.ini
├── src/                    # Source code
├── tests/                  # Test suite
└── docs/                   # Documentation
```

**Backward Compatibility**: The ConversationMemoryServer automatically detects whether to use the new `data/` structure or legacy structure for existing installations.

**External Storage**: Claude Desktop integration still uses `~/claude-memory/` (outside project) for user conversation storage.

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

### SonarCloud Quality Gate

Recent fixes applied to resolve code quality issues:
- ✅ Replaced bare except clauses with specific exception types
- ✅ Removed unused import statements
- ✅ Extracted magic numbers to named constants
- ✅ Broke down complex methods (generate_weekly_summary)
- ✅ Added path validation for security
- ✅ Migrated from self-hosted SonarQube to SonarCloud for public visibility
- ✅ Fixed return type hint for add_conversation method
- ✅ Reduced cognitive complexity in search_conversations method
- ✅ Excluded archive/ and scripts/ folders from code analysis
- ✅ Added proper file formatting (newlines at end of files)

**SonarCloud Configuration:**
- Organization: adamkwhite
- Project Key: adamkwhite_claude-memory-mcp
- Dashboard: https://sonarcloud.io/summary/overall?id=adamkwhite_claude-memory-mcp
- Exclusions: `tests/**,**/*test*.py,**/test_*.py,**/*benchmark*.py,**/*performance*.py,scripts/**,**/__pycache__/**,htmlcov/**,archive/**,examples/**,docs/generated/**,benchmark_results/**`

**Current Test Coverage: 98.68%** | Duplications: **7%**

**Coverage Milestones Achieved:**
- ✅ **conversation_memory.py**: 100% coverage
- ✅ **exceptions.py**: 100% coverage  
- 🎯 **Total Project**: 98.68% coverage (11 lines remaining)
- 📈 **Progress**: Achieved near-perfect coverage

**SonarCloud Exclusion Workflow:**
When creating new files, automatically check if they need SonarCloud coverage analysis:

**Files that DON'T need coverage (auto-exclude):**
- Tests: `tests/*`, `test_*.py`, `*_test.py`, `*benchmark*.py`, `*performance*.py`
- Scripts: `scripts/*`, `*.sh`, utility files  
- Generated: `docs/generated/*`, `benchmark_results/*`
- Examples: `examples/*`
- Build artifacts: `build/*`, `dist/*`, `__pycache__/*`

**Process:**
1. Before creating files, identify if they need coverage analysis
2. If not, immediately update sonar-project.properties exclusions
3. Use descriptive naming that fits existing exclusion patterns
4. **Update ALL GitHub workflow actions** that run tests to exclude non-coverage files
5. Commit exclusion updates with main file changes
6. This prevents coverage drops and eliminates reactive fixes

**GitHub Workflow Update Requirements:**
When adding exclusions, also update these workflow files:
- `.github/workflows/build.yml` - Main coverage workflow (exclude from `--ignore` in pytest)
- `.github/workflows/performance.yml` - Performance testing (runs separately)
- Any other workflows running pytest with coverage

### Environment Setup

```bash
# Use Python 3.11 for this project
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest pytest-cov pytest-asyncio
```

## Testing Strategy

**Test Suite Organization:**
- `test_100_percent_coverage.py` - Essential for edge cases, error handling, and security validation. DO NOT remove.
- `test_memory_server.py` - Functional testing of core memory server features
- `test_direct_coverage.py` - Direct testing of server components
- `test_fastmcp_coverage.py` - FastMCP-specific functionality testing
- `test_server.py` - Integration testing of complete server functionality
- `standalone_test.py` - Manual test script (excluded from pytest)

**Coverage Monitoring:**
- Local: Run `pytest tests/ --ignore=tests/standalone_test.py --cov=src --cov-report=term`
- CI: GitHub Actions runs all tests and reports to SonarCloud
- Target: 90%+ coverage maintained through layered testing approach

**PR Quality Gate Enforcement:**
- All PRs trigger GitHub Actions workflow with SonarCloud analysis
- PRs are blocked if tests fail or SonarCloud quality gate fails
- Quality gate enforces: Coverage on New Code ≥ 90%
- Failed quality gates prevent PR merging (requires branch protection rules)
- This ensures all new code meets quality standards before merge

## Git Workflow

**MANDATORY:** This repository has branch protection rules that REQUIRE pull requests for all changes to main:

### **Standard Development Workflow (REQUIRED):**
```bash
# 1. Create feature branch (ALWAYS REQUIRED - even for documentation changes)
git checkout -b feature/your-feature-name

# 2. Make changes and commit
git add <files>
git commit -m "descriptive message"

# 3. **MANDATORY: Run full test suite after major changes**
# Activate virtual environment and run tests
source claude-memory-mcp-venv/bin/activate
python -m pytest tests/ --ignore=tests/standalone_test.py --cov=src --cov-report=term -v

# 4. Push branch to GitHub (NEVER push directly to main)
git push origin feature/your-feature-name

# 5. Open Pull Request on GitHub
# - ALWAYS mention @claude in PR body or comments for review
# - PR triggers automated testing and SonarCloud analysis
# - Must pass all quality gates before merge is allowed
# - Coverage on new code must be ≥ 90%

# 6. Merge PR (only after quality gates pass)
# - Tests must pass ✅
# - SonarCloud quality gate must pass ✅
# - PR conversations must be resolved ✅
```

### **CRITICAL: No Direct Pushes to Main**
- ❌ **ALL direct pushes to main are BLOCKED** - even for simple documentation updates
- ❌ **Force pushes are BLOCKED** 
- ❌ **Quality gate failures block merges**
- ✅ **EVERY change must go through feature branch + PR process**
- ⚠️ **This applies to todos.md, README.md, and ALL files without exception**

### **Quality Gate Requirements:**
- All tests must pass
- SonarCloud analysis must pass
- Coverage on new code ≥ 90%
- No unresolved PR conversations
- Linear history maintained

**Note:** Even repository owners cannot bypass these rules - this ensures enterprise-grade quality standards.

### **Mandatory Testing Requirements**

**ALWAYS run full test suite for these changes:**
- Any code changes to `src/` directory
- Directory structure modifications
- Configuration file updates (`pyproject.toml`, `pytest.ini`)
- Database schema changes
- API endpoint modifications
- New feature implementations
- Bug fixes involving core functionality

**Testing Command (Copy-Paste Ready):**
```bash
source claude-memory-mcp-venv/bin/activate && python -m pytest tests/ --ignore=tests/standalone_test.py --cov=src --cov-report=term -v
```

**Expected Results:**
- ✅ All tests must pass (191/191 or more)
- ✅ Coverage should be ≥ 94% (current baseline)
- ✅ No failing tests before creating PR

**If tests fail:**
1. Fix failing tests immediately
2. Re-run test suite until all pass
3. Only then proceed with PR creation

This prevents back-and-forth in PRs due to test failures.

### **⚠️ CRITICAL: Lessons Learned from Process Failures**

**Based on SQLite FTS Search Optimization implementation (June 2025), the following workflow violations caused significant impact:**

**NEVER DO THIS:**
- ❌ Skip local testing before commits ("I'll test in CI/CD")
- ❌ Push changes without running full test suite first
- ❌ Create reactive "fix-as-we-go" PRs with multiple failure cycles
- ❌ Submit PRs before validating compatibility with existing systems
- ❌ Ignore async compatibility analysis for major changes

**CONSEQUENCES OF WORKFLOW VIOLATIONS:**
- **Technical Impact**: 64+ test failures, hours of reactive debugging
- **Team Impact**: Multiple back-and-forth cycles, wasted review time
- **Process Impact**: CI/CD pipeline blocked, delayed other features
- **Quality Impact**: Reactive fixes instead of systematic solutions

**MANDATORY PREVENTIVE MEASURES:**
1. **Pre-Commit Validation**: ALWAYS run local test suite before first commit
2. **Compatibility Analysis**: Plan async/breaking changes before implementation
3. **Script Dependencies**: Test all supporting scripts locally before CI/CD
4. **Systematic Approach**: Complete planning phase before coding phase
5. **Zero-Defect PRs**: Only submit PRs after local validation passes

**ACCOUNTABILITY:**
- Local testing is **NON-NEGOTIABLE** - no exceptions for "minor" changes
- "Speed over quality" approach is **explicitly prohibited**
- Process shortcuts that create technical debt are **unacceptable**
- Reactive debugging in PRs indicates **insufficient upfront planning**

### **📋 PRE-COMMIT CHECKLIST (MANDATORY)**

**Before making ANY commit to ANY branch:**

- [ ] **1. Run Full Test Suite Locally**
  ```bash
  source claude-memory-mcp-venv/bin/activate && python -m pytest tests/ --ignore=tests/standalone_test.py --cov=src --cov-report=term -v
  ```
- [ ] **2. Verify All Tests Pass** (expect 417+ passing tests)
- [ ] **3. Check Coverage Baseline** (expect ≥76% coverage)
- [ ] **4. Test Supporting Scripts** (if modified any scripts/ files)
- [ ] **5. Validate Async Compatibility** (if modified async methods)
- [ ] **6. Run SonarCloud Analysis** (triggered automatically on PR)
- [ ] **7. Document Breaking Changes** (if any API changes)

**Before creating ANY Pull Request:**

- [ ] **8. Re-run Full Test Suite** (final validation)
- [ ] **9. Review All Changed Files** (ensure no debug code, console.log, etc.)
- [ ] **10. Write Descriptive PR Description** (what, why, how, testing done)
- [ ] **11. Self-Review Changes** (would you approve this PR?)
- [ ] **12. Verify No Merge Conflicts** (rebase if needed)

**⚠️ ZERO TOLERANCE:** Committing without completing this checklist violates workflow standards and creates technical debt.

**GitHub Actions Workflow Notes:**
- ✅ **Migrated to SonarCloud**: Public code quality dashboard with automatic PR decoration
- **Two build phases**: PR testing (cannot push) + post-merge execution (can push badges)
- **Badge updates**: SonarCloud badges auto-update from cloud platform
- **PR builds**: Test code without attempting repository modifications

## 100% Test Coverage Initiative

**Current Status: 98.68% coverage (SUFFICIENT - no longer pursuing 100%)**

### Coverage Breakdown by Module
- `conversation_memory.py`: **100%** ✅ (237 lines, 0 missing)
- `exceptions.py`: **100%** ✅ (10 lines, 0 missing)  
- `server_fastmcp.py`: **99.01%** (405 lines, 4 missing)
- `validators.py`: **98.65%** (74 lines, 1 missing)
- `logging_config.py`: **94.44%** (108 lines, 6 missing)

### Implementation Strategy
**Phase 1: Exception Handling (COMPLETED ✅)**
- Target: ImportError blocks, JSON processing errors
- Achievement: conversation_memory.py → 100% coverage
- Progress: 95.08% → 96.52% total coverage

**Phase 2: Edge Cases (COMPLETED ✅)**
- Target: validators.py line 104, server_fastmcp.py key lines
- Achievement: 96.52% → 97.96% total coverage  

**Phase 3: Integration Testing (COMPLETED ✅)**
- Target: logging_config.py remaining lines
- Achievement: 97.96% → 98.68% total coverage

### Test Modules for Coverage
- `test_importerror_coverage.py` - ImportError exception paths
- `test_json_exception_coverage.py` - JSON processing edge cases  
- `test_validator_edge_cases.py` - Input validation boundaries
- `test_100_percent_coverage.py` - Comprehensive edge case testing

## Implementation Details

### Universal Memory Architecture
The system uses a pluggable importer architecture where each AI platform has a dedicated importer class inheriting from `BaseImporter`:

- **BaseImporter**: Abstract base defining universal conversation format
- **Format Detection**: Automatic platform recognition with confidence scoring
- **Schema Validation**: JSON schemas ensure data integrity and compatibility
- **Universal Format**: Standardized internal representation for cross-platform compatibility

### Key Design Decisions
- **Backward Compatibility**: Existing Claude conversations remain fully functional
- **Privacy-First Development**: Tools for sanitizing real export data for testing
- **Extensible Architecture**: Easy addition of new AI platforms
- **Performance-Optimized**: SQLite FTS5 for sub-3ms search times

## Next Steps

**Immediate Priorities (Next Session):**
1. **Test Additional Platforms** - Validate Cursor/Claude importers with real export data
2. **Complete Schema Validation** - Finish JSON schemas for all supported platforms
3. **FastMCP Integration** - Wire up importers to MCP server with new tools
4. **End-to-End Testing** - Full import pipeline validation and performance benchmarking

**Medium-Term Goals:**
- Real-time platform integrations (ChatGPT API, Cursor sessions)
- Advanced search features (date filtering, semantic search)
- Multi-user support and workspace isolation
- Cross-platform conversation sync and merging

## Recent Changes

### **October 10, 2025 - SonarCloud Async Compliance & Code Quality ✅**

**PRs Merged: #69, #70**
- **Achievement**: Resolved all SonarCloud code quality issues and async/await warnings
- **Impact**: 100% compliant with SonarCloud quality gates, proper async file I/O throughout

**Async File I/O Migration:**
- ✅ Converted `add_conversation()` to use `async with aiofiles.open()`
- ✅ Converted `generate_weekly_summary()` to async file writes
- ✅ Converted `search_conversations()` fallback path to async
- ✅ Converted `search_by_topic()` and `_search_topic_json()` to async
- ✅ Converted `_process_conversation_for_search()` to async
- ✅ Added `aiofiles>=24.1.0` dependency

**Code Quality Improvements:**
- ✅ Extracted `ISO_DATETIME_FORMAT` constant (logging_config.py)
- ✅ Removed redundant `list()` call (cursor_importer.py)
- ✅ Removed unused parameter (generic_importer.py)
- ✅ Changed HTTP to HTTPS in schema URL (chatgpt_schema.py)

**Test Coverage Enhancements:**
- ✅ Added `test_search_by_topic_json_fallback` - JSON topic search coverage
- ✅ Added `test_search_conversations_json_fallback` - Linear search coverage
- ✅ Added `test_search_with_missing_file` - Error handling coverage
- ✅ Achieved 80%+ coverage on new code (SonarCloud requirement)

**CI/CD Results:**
- ✅ All 435 tests passing (was 417)
- ✅ 78% overall coverage (was 76%)
- ✅ Zero code smells, zero security hotspots
- ✅ All SonarCloud quality gates passing

## Recent Changes (June 15, 2025)

### **🎯 MAJOR MILESTONE: Universal Memory MCP Framework - PRODUCTION READY ✅**

**Complete System Implementation Achieved:**
- **417 Tests Passing** - Comprehensive test coverage with zero failures
- **76% Overall Coverage** - Major improvement from 50% baseline after adding new framework
- **CI/CD Fully Functional** - GitHub Actions pipeline operational with SonarCloud integration
- **Public Code Quality Dashboard** - Clean codebase with zero code smells/security issues visible to recruiters

### **Universal Memory MCP Framework Implementation ✅ MAJOR FEATURE**
- **Achievement**: Complete architecture transformation from Claude-specific to universal AI platform support
- **Scope**: 13 new files implementing extensible import framework + comprehensive test suite
- **Impact**: Foundation for supporting all major AI platforms with standardized conversation management

**Core Components Implemented:**
- `src/format_detector.py` - Automatic platform recognition with confidence scoring (83% coverage)
- `src/importers/` - Complete pluggable importer system (5 classes, 75-86% coverage each)
- `src/schemas/chatgpt_schema.py` - Production-ready ChatGPT validation (57% coverage)
- `docs/ai_platform_formats.md` - Comprehensive platform format research
- `scripts/sanitize_chatgpt_export.py` - Privacy-safe development tools

**Test Suite Excellence (June 15, 2025):**
- **28 Test Classes** - Comprehensive coverage across all importer components
- **417 Individual Tests** - Detailed edge case and integration testing
- **Real Format Validation** - Tests using actual AI platform export structures
- **Mock Integration** - Proper isolation testing with comprehensive mocking
- **CI Pipeline Integration** - All tests pass in GitHub Actions environment

**Coverage Achievements:**
- `format_detector.py`: 40% → 83% (+43% improvement)
- `generic_importer.py`: 13% → 86% (+73% improvement) 
- `chatgpt_schema.py`: 0% → 57% (+57% improvement)
- `cursor_importer.py`: 13% → 84% (+71% improvement)
- `claude_importer.py`: 15% → 75% (+60% improvement)

**ChatGPT Integration (Production Ready):**
- Full OpenAI export format support with complex message mapping structure
- JSON schema validation tested against real ChatGPT exports
- Privacy-safe sanitization tools for development with actual user data
- Handles conversation arrays, message nodes, and metadata preservation

**Development Excellence:**
- Real export structure analysis revealing complex mapping-based message storage
- Comprehensive error handling and validation with detailed feedback
- Privacy-first approach with tools for safe development using real data
- Extensible design ready for additional platform implementations

### **Critical System Fixes (June 15, 2025)**
- **Merge Conflict Resolution**: Successfully resolved conflicts in generic_importer.py and schemas/__init__.py
- **Test Framework Stabilization**: Fixed all 20 failing tests through systematic debugging
- **CI/CD Pipeline Repair**: Added missing jsonschema dependency to fix GitHub Actions failures
- **SonarCloud Migration**: Migrated from self-hosted SonarQube to public SonarCloud dashboard for visibility

### **Previous Major Fix: MCP JSON Parsing (PR #33)**

### **Search Optimization Implementation ✅ MAJOR PERFORMANCE IMPROVEMENT**
- **Achievement**: Implemented SQLite FTS5 full-text search replacing linear search
- **Performance**: 4.4x faster search with 77.5% performance improvement
- **Features**:
  - SQLite FTS5 database with full-text search and relevance scoring
  - Automatic migration from JSON to SQLite with verification
  - Backward compatibility with fallback to linear search
  - New MCP tools: `get_search_stats`, `search_by_topic`
  - **Note**: `migrate_to_sqlite` tool disabled by default (saves 573 tokens context) - SQLite auto-migrates on first use
- **Testing**: Comprehensive test suite covering all SQLite functionality
- **Scalability**: Search now scales efficiently with conversation growth

### **Previous Major Fix: MCP JSON Parsing (PR #33)**
- **Problem Solved**: Claude Desktop MCP communication restored
- **Root Cause**: Print statements corrupting JSON-RPC protocol
- **Solution**: Proper logging configuration with `~/.claude-memory/logs/claude-mcp.log`
- **Impact**: MCP server fully functional with Claude Desktop

### **Current Status**
- **Branch**: `feature/search-optimization-analysis`
- **Test Coverage**: 98.68% (industry-leading)
- **Code Quality**: 0 code smells, 0 security hotspots
- **Search Performance**: SQLite FTS5 enabled (4.4x faster than linear)
- **Production Ready**: High-performance search with SQLite optimization

### **Completed Major Features**
1. ✅ **SQLite FTS Search** - 4.4x performance improvement with full-text search
2. ✅ **Path Portability** - Universal deployment support (PRs #36, #37, #38)
3. ✅ **Test Coverage** - 98.68% with comprehensive edge case testing
4. ✅ **Input Validation** - Security-focused validation preventing attacks
5. ✅ **MCP Integration** - Claude Desktop compatibility with proper logging

### **Next Steps (Medium Priority)**
1. **Universal Memory MCP** - Expand to support ChatGPT, Cursor, and other AI platforms
2. **Advanced Search Features** - Add date filtering, advanced queries, and search suggestions
3. **Performance Monitoring** - Add real-time performance metrics and search analytics
4. **Multi-user Support** - Architecture for supporting multiple users/sessions

### **Technical Excellence Achieved**
- **Search Performance**: Sub-3ms search times vs 10ms+ linear search
- **Scalability**: Efficient indexing handles large conversation datasets
- **Reliability**: Dual storage (JSON + SQLite) with automatic fallback
- **Security**: Comprehensive input validation and path security

## Project Management

**Task Tracking:** All todos and project tasks are maintained in `todos.md` for persistence across Claude Code sessions. This includes pending improvements, completed work, and priority classifications.

**Implementation Plans:** Major features use Cornell numbering system for systematic implementation:
- **Format**: `1.1.1`, `2.3.2`, etc. for hierarchical task organization
- **Structure**: 9 major sections, each with 2-4 subsections, each with 3-5 specific tasks
- **Purpose**: Enables intermediate developers to implement complex features step-by-step
- **Examples**: Encryption (69 tasks), Path Portability (46 tasks), SonarCloud Migration (46 tasks), Project Cleanup (57 tasks)
- **Benefits**: Clear progress tracking, logical task dependencies, comprehensive coverage

**Plan Creation Guidelines:**
- Use Cornell numbering for all multi-step implementation plans
- Break complex features into 9 logical sections
- Provide 40-70 specific, actionable subtasks
- Include testing, documentation, and validation requirements
- Maintain quality standards throughout implementation

## MCP Server Deployment Notes

### **Local Development**

**From project root directory:**
```bash
# Install dependencies
python3 -m venv claude-memory-mcp-venv
source claude-memory-mcp-venv/bin/activate
pip install -e .

# Run server directly
python3 src/server_fastmcp.py

# Enable console logging for debugging
CLAUDE_MCP_CONSOLE_OUTPUT=true python3 src/server_fastmcp.py
```

**From src/ directory:**
```bash
# Create virtual environment (if not exists)
python3 -m venv ../claude-memory-mcp-venv

# Install dependencies and run server
source ../claude-memory-mcp-venv/bin/activate && pip install -e .. && python3 server_fastmcp.py

# Or if already installed, just run server
source ../claude-memory-mcp-venv/bin/activate && python3 server_fastmcp.py
```

### **Claude Desktop Integration**
Add to Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "claude-memory": {
      "command": "python",
      "args": ["/absolute/path/to/claude-memory-mcp/src/server_fastmcp.py"],
      "cwd": "/absolute/path/to/claude-memory-mcp"
    }
  }
}
```

**Log Location**: `~/.claude-memory/logs/claude-mcp.log`  
**Storage Location**: `~/claude-memory/conversations/`