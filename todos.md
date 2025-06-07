# Project Todos

This file maintains persistent todos across Claude Code sessions.

## High Priority - Critical Issues

- [x] Fix Python environment - upgrade to 3.11+ and install missing MCP dependencies (mcp[cli]>=1.9.2)
- [x] Remove code duplication - extract common ConversationMemoryServer class from server_fastmcp.py and standalone_test.py (~400 lines)
- [x] Update GitHub Actions to use Python 3.11+ instead of 3.10
- [x] Fix path security vulnerability - add path validation and sanitization to prevent path traversal attacks
- [x] Replace bare exception handling - use specific exceptions instead of bare 'except:' blocks
- [ ] Fix failing tests - resolve 4 test failures related to imports and date-sensitive assertions

## Medium Priority - Code Quality & Performance

- [ ] **Investigate remaining 9 code smells reported by SonarQube**
  - Current: 9 code smells showing in latest analysis
  - Goal: Reduce to 0 or minimal acceptable level
  - Focus areas: Check for any remaining complexity, duplication, or maintainability issues
- [ ] Optimize search performance - replace linear search with proper indexing (SQLite FTS or inverted index)
- [ ] Add input validation - validate conversation content, titles, and other user inputs
- [ ] Implement centralized configuration management system
- [ ] Add proper logging throughout the application
- [ ] Remove hard-coded system paths to improve portability

## Low Priority - Enhancements

- [ ] **Monitor SonarQube quality gate status after latest fixes**
  - Verify all quality gates are now passing
  - Confirm coverage metrics are accurate with archive/scripts exclusions
  - Check that all recent fixes resolved the "8 Issues > 0" condition
- [ ] **Consider improving test coverage from 80.2% to 85%+**
  - Current: 80.2% coverage
  - Target: 85%+ for better code reliability
  - Focus on testing edge cases and error handling paths
- [ ] Implement conversation data encryption for security
- [ ] Add caching strategy for file I/O operations to improve performance
- [ ] Migrate from JSON files to SQLite database for better performance and indexing
- [ ] Clean up project structure - consolidate duplicate scripts and remove archive files

## Completed Todos

- [x] Create todos.md file for persistent todo storage (HIGH)
- [x] Check if todos.md already exists and load existing todos (HIGH)
- [x] Analyze codebase and identify improvement areas
- [x] Fixed README badge URLs to point to correct SonarQube instance
- [x] Extracted magic numbers to named constants
- [x] Broke down complex methods (generate_weekly_summary)
- [x] Fixed return type hint for add_conversation method
- [x] Reduced cognitive complexity in search_conversations method
- [x] Excluded archive/ and scripts/ folders from SonarQube analysis
- [x] Added proper file formatting (newlines at end of files)

---
*Last updated: 2025-01-06*