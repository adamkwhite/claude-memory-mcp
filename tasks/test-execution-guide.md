# Test Execution Guide: Claude Conversation Memory MCP Server

## Overview

This guide provides a structured approach to testing your Claude Conversation Memory MCP Server using both exploratory session-based testing and structured test procedures. The testing is designed to focus on your high-priority risks (security and compatibility) while providing comprehensive coverage in ~6 hours total effort.

---

## Testing Materials Overview

### 📋 Documentation Created

**Strategic Documents:**
- `test-strategy.md` - Overall test approach and risk assessment
- `session-charters.md` - Five focused exploratory testing sessions
- `session-templates.md` - Templates for documenting your testing

**Structured Test Suites:**
- `structured-tests/security-tests.md` - Step-by-step security testing procedures
- `structured-tests/integration-tests.md` - FastMCP and Claude Desktop integration tests
- `structured-tests/functional-tests.md` - Core functionality validation tests

### 🎯 Priority-Based Testing Approach

**HIGH PRIORITY (Must Do)**
- Session 1: Security & Data Protection (90 min)
- Session 2: FastMCP Integration (60 min)

**MEDIUM PRIORITY (Should Do)**  
- Session 3: Core Functionality (90 min)
- Session 4: Edge Cases & Error Handling (60 min)

**LOW PRIORITY (Nice to Do)**
- Session 5: Performance & Scale (60 min)

---

## Recommended Testing Sequence

### Phase 1: Critical Risk Validation (2.5 hours)

#### Week 1, Day 1: Security Session
**Duration:** 90 minutes  
**Focus:** Data protection and file system security  
**Charter:** Use Session 1 from `session-charters.md`  

**Pre-session Setup (10 min):**
1. Backup current conversation data: `cp -r ~/claude-memory ~/claude-memory-backup`
2. Prepare test environment with monitoring
3. Review security test cases in `structured-tests/security-tests.md`

**Session Execution (70 min):**
- Follow Session 1 charter for exploratory security testing
- Use SEC-001 through SEC-005 from structured tests as needed
- Document using session sheet template

**Post-session (10 min):**
- Complete session report
- File any critical security bugs found
- Plan remediation if needed

#### Week 1, Day 2: Integration Session  
**Duration:** 60 minutes  
**Focus:** FastMCP protocol and Claude Desktop compatibility  
**Charter:** Use Session 2 from `session-charters.md`

**Pre-session Setup (10 min):**
1. Ensure MCP server running and connected to Claude Desktop
2. Prepare integration test scenarios from `structured-tests/integration-tests.md`
3. Set up connection monitoring

**Session Execution (45 min):**
- Test FastMCP protocol compliance 
- Verify Claude Desktop integration
- Explore error handling and recovery

**Post-session (5 min):**
- Document integration status
- Note any compatibility issues

### Phase 2: Functional Validation (2.5 hours)

#### Week 1, Day 3: Core Functionality Session
**Duration:** 90 minutes  
**Charter:** Use Session 3 from `session-charters.md`

**Focus Areas:**
- Search accuracy and relevance
- Conversation storage and indexing  
- Weekly summary generation
- Data persistence and integrity

**Testing Approach:**
- Use exploratory charter as guide
- Reference functional tests for specific scenarios
- Test realistic user workflows

#### Week 1, Day 4: Edge Cases Session
**Duration:** 60 minutes  
**Charter:** Use Session 4 from `session-charters.md`

**Focus Areas:**
- Boundary conditions and error handling
- Malformed inputs and recovery
- File system error scenarios
- Data corruption resistance

### Phase 3: Performance Validation (1 hour)

#### Week 1, Day 5: Performance Session (Optional)
**Duration:** 60 minutes  
**Charter:** Use Session 5 from `session-charters.md`

**Focus Areas:**
- Response time under load
- Memory usage patterns
- Scalability limits
- Concurrent operation handling

---

## How to Use the Testing Materials

### Exploratory Sessions (Primary Approach)

**Session Preparation:**
1. Read the charter from `session-charters.md`
2. Set up test environment as specified
3. Prepare session sheet from `session-templates.md`
4. Time-box the session (use timer)

**During Session:**
1. Follow charter mission as primary guide
2. Take notes in session sheet as you test
3. Follow interesting bugs even if off-charter
4. Apply multiple test techniques (function, risk, domain, etc.)
5. Document bugs and issues as you find them

**After Session:**
1. Complete session sheet within 10 minutes
2. Use debrief checklist to validate session quality
3. File formal bug reports for significant issues
4. Plan follow-up sessions based on findings

### Structured Tests (Supporting Approach)

**When to Use:**
- Need systematic coverage of specific areas
- Want repeatable test procedures
- Investigating specific bugs found during exploratory sessions
- Need detailed security or integration validation

**How to Execute:**
1. Choose appropriate test suite based on current focus
2. Follow step-by-step procedures
3. Document results in test suite or session notes
4. Use structured results to inform exploratory testing

### Hybrid Approach (Recommended)

**Combine Both Methods:**
- Start sessions with exploratory charter
- Use structured tests when you need specific coverage
- Reference structured tests during exploratory work
- Document everything in session sheets

---

## Test Environment Setup

### Initial Setup
```bash
# Backup existing data
cp -r ~/claude-memory ~/claude-memory-backup-$(date +%Y%m%d)

# Verify environment
cd ~/Code/claude-memory-mcp
python --version
pip list | grep fastmcp
ls -la ~/claude-memory/

# Start MCP server
python server_fastmcp.py
```

### Test Data Preparation
```bash
# Create test conversation samples
mkdir -p ~/test-data/conversations
# Use add_conversation tool to create known test data
# Or prepare sample conversations in advance
```

### Monitoring Setup
```bash
# Monitor file system during testing
tail -f ~/claude-memory-mcp/mcp-server.log &

# Check resource usage
htop  # or top for system monitoring
```

---

## Bug Reporting Guidelines

### Bug Severity Classification

**Critical (Stop Testing)**
- Data loss or corruption
- Security vulnerabilities exposing personal data
- System crashes or complete failures
- FastMCP integration completely broken

**High (Report Immediately)**
- Feature doesn't work as specified in PRD
- Search returns incorrect results
- File system errors or permission issues
- Performance completely unacceptable

**Medium (Report in Session)**
- Minor functional issues
- Usability problems
- Error messages unclear
- Performance degradation

**Low (Note in Session)**
- Cosmetic issues
- Minor inconsistencies
- Enhancement opportunities

### Bug Report Template
```markdown
**Title:** [Concise description of the problem]

**Severity:** [Critical/High/Medium/Low]

**Environment:** 
- Ubuntu 20.04 WSL
- Claude Desktop [version]
- MCP Server commit: [hash if available]

**Steps to Reproduce:**
1. [Clear, numbered steps]
2. [Include exact commands/inputs used]
3. [Specify any required test data]

**Expected Result:** [What should happen]

**Actual Result:** [What actually happened]

**Security/Privacy Impact:** [If applicable]

**Workaround:** [If known]

**Additional Notes:** [Any other relevant information]
```

---

## Session Success Metrics

### Per Session
- **Time Management:** Stay within charter time box (±15 minutes)
- **Coverage:** Address charter mission adequately
- **Discovery:** Find bugs or gain confidence in tested areas
- **Documentation:** Complete session sheet within 10 minutes of session end

### Overall Testing Success
- **Security:** No critical data exposure risks identified
- **Integration:** FastMCP works reliably with Claude Desktop
- **Functionality:** Core tools work for intended use cases
- **Confidence:** Comfortable deploying for personal use

### Go/No-Go Decision Points

**GO Criteria:**
- No critical security issues found
- Claude Desktop integration functional
- Core workflows (search, add, summarize) work reliably
- Performance acceptable for personal use (searches < 10 seconds)

**NO-GO Criteria:**
- Data exposure or security risks
- FastMCP integration failures
- Core functionality broken or unreliable
- Significant data loss or corruption risks

---

## Getting Help During Testing

### When Stuck
1. Take a 5-minute break and review charter
2. Try a different test technique from the strategy
3. Reference structured tests for systematic approaches
4. Use PROOF debrief agenda to think through the session

### Documentation Issues
1. Better to have incomplete but honest notes than perfect fiction
2. Use bullet points and keywords during active testing
3. Expand notes immediately after session
4. Focus on what you actually did and observed

### Charter Problems
1. It's okay to change charter to match actual work done
2. Document charter changes in session notes
3. Create new charter for interesting areas discovered
4. Don't force artificial adherence to original charter

---

**Execution Guide Version:** 1.0  
**Total Estimated Effort:** 6 hours across 5 sessions  
**Prerequisites:** MCP server functional, Claude Desktop configured  
**Last Updated:** 2025-06-01