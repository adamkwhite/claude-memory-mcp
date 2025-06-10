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
- Exclusions: `tests/**,**/*test*.py,**/test_*.py,**/*benchmark*.py,**/*performance*.py,scripts/**,**/__pycache__/**,htmlcov/**,archive/**,examples/**,docs/generated/**,benchmark_results/**`

**Current Test Coverage: 95.32%** | Duplications: **7%**

**Coverage Milestones Achieved:**
- ✅ **conversation_memory.py**: 100% coverage (Phase 1 complete)
- ✅ **exceptions.py**: 100% coverage  
- 🎯 **Total Project**: 95.32% coverage (39 lines remaining)
- 📈 **Progress**: 95.08% → 95.32% (Phase 1 achievements)

**SonarQube Exclusion Workflow:**
When creating new files, automatically check if they need SonarQube coverage analysis:

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
- All PRs trigger GitHub Actions workflow with SonarQube analysis
- PRs are blocked if tests fail or SonarQube quality gate fails
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

# 3. Push branch to GitHub (NEVER push directly to main)
git push origin feature/your-feature-name

# 4. Open Pull Request on GitHub
# - ALWAYS mention @claude in PR body or comments for review
# - PR triggers automated testing and SonarQube analysis
# - Must pass all quality gates before merge is allowed
# - Coverage on new code must be ≥ 90%

# 5. Merge PR (only after quality gates pass)
# - Tests must pass ✅
# - SonarQube quality gate must pass ✅
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
- SonarQube analysis must pass
- Coverage on new code ≥ 90%
- No unresolved PR conversations
- Linear history maintained

**Note:** Even repository owners cannot bypass these rules - this ensures enterprise-grade quality standards.

**Why this is needed:**
- GitHub Actions automatically updates `.badges/*.svg` files after each push
- SonarQube analysis runs and commits updated metrics badges
- Without pulling first, pushes will be rejected with "fetch first" errors
- This is normal behavior and indicates SonarQube improvements are working

## 100% Test Coverage Initiative

**Current Status: 95.32% coverage (39 lines remaining)**

### Coverage Breakdown by Module
- `conversation_memory.py`: **100%** ✅ (237 lines, 0 missing)
- `exceptions.py`: **100%** ✅ (10 lines, 0 missing)  
- `server_fastmcp.py`: **93.58%** (405 lines, 26 missing)
- `validators.py`: **98.65%** (74 lines, 1 missing)
- `logging_config.py`: **88.89%** (108 lines, 12 missing)

### Implementation Strategy
**Phase 1: Exception Handling (COMPLETED ✅)**
- Target: ImportError blocks, JSON processing errors
- Achievement: conversation_memory.py → 100% coverage
- Progress: 95.08% → 95.32% total coverage

**Phase 2: Edge Cases (IN PROGRESS)**
- Target: validators.py line 104, server_fastmcp.py key lines
- Goal: 97-98% total coverage  

**Phase 3: Integration Testing (PLANNED)**
- Target: logging_config.py remaining lines
- Goal: 100% total coverage

### Test Modules for Coverage
- `test_importerror_coverage.py` - ImportError exception paths
- `test_json_exception_coverage.py` - JSON processing edge cases  
- `test_validator_edge_cases.py` - Input validation boundaries
- `test_100_percent_coverage.py` - Comprehensive edge case testing

## Project Management

**Task Tracking:** All todos and project tasks are maintained in `todos.md` for persistence across Claude Code sessions. This includes pending improvements, completed work, and priority classifications.

**Implementation Plans:** Major features use Cornell numbering system for systematic implementation:
- **Format**: `1.1.1`, `2.3.2`, etc. for hierarchical task organization
- **Structure**: 9 major sections, each with 2-4 subsections, each with 3-5 specific tasks
- **Purpose**: Enables intermediate developers to implement complex features step-by-step
- **Examples**: Encryption (69 tasks), Path Portability (46 tasks), SonarQube Workflow (46 tasks), Project Cleanup (57 tasks)
- **Benefits**: Clear progress tracking, logical task dependencies, comprehensive coverage

**Plan Creation Guidelines:**
- Use Cornell numbering for all multi-step implementation plans
- Break complex features into 9 logical sections
- Provide 40-70 specific, actionable subtasks
- Include testing, documentation, and validation requirements
- Maintain quality standards throughout implementation