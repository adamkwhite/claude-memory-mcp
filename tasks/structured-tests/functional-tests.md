# Functional Test Suite: Claude Conversation Memory MCP Server

## Test Suite Overview
This suite validates the core functionality of the three main MCP tools: search_conversations, add_conversation, and generate_weekly_summary. These tests verify the system meets its functional requirements.

---

## FUNC-001: Search Conversations Testing

**Objective**: Verify search functionality returns accurate, relevant results with proper ranking and formatting.

### Test Data Setup
Create test conversations with known content for predictable search results:

```bash
# Set up test data (execute these via MCP tools)
Test Conversation 1: "Python programming tutorial covering functions, classes, and modules"
Test Conversation 2: "JavaScript async programming with promises and async/await"  
Test Conversation 3: "Database design principles and SQL optimization techniques"
Test Conversation 4: "Machine learning fundamentals using Python and scikit-learn"
Test Conversation 5: "Web development with React and Node.js backend services"
```

### Test Cases

#### FUNC-001.1: Basic Search Functionality
**Steps:**
1. Execute search_conversations with query: "python"
2. Verify results include conversations 1 and 4
3. Check result format includes title, date, topics, score, preview
4. Execute search_conversations with query: "javascript" 
5. Verify results include conversations 2 and 5

**Expected Results**:
- Python query returns 2 relevant conversations
- JavaScript query returns 2 relevant conversations  
- Results properly formatted with all required fields

**Pass/Fail Criteria**: PASS if correct conversations returned with proper format, FAIL if missing results or format issues

---

#### FUNC-001.2: Search Relevance Scoring
**Steps:**
1. Search for "python programming" (should match conversation 1 closely)
2. Compare relevance scores between conversations 1 and 4
3. Search for exact phrase match vs. partial match
4. Verify higher scores for better matches

**Expected Results**: Conversation 1 scores higher than conversation 4 for "python programming"

**Pass/Fail Criteria**: PASS if relevance scoring logical, FAIL if poor scoring

---

#### FUNC-001.3: Search Result Limits
**Steps:**
1. Create additional test conversations (6+ total)
2. Execute search with limit=3, verify only 3 results returned
3. Execute search with limit=1, verify only 1 result returned
4. Execute search with limit=10, verify all relevant results returned (up to 10)
5. Test with limit=0 and negative limits

**Expected Results**: Limit parameter properly controls result count

**Pass/Fail Criteria**: PASS if limits respected, FAIL if incorrect result counts

---

#### FUNC-001.4: Topic-Based Search
**Steps:**
1. Search for specific topics that should be auto-extracted:
   - "sql" (should find conversation 3)
   - "react" (should find conversation 5)
   - "machine learning" (should find conversation 4)
2. Verify topic matching increases relevance scores
3. Check topics are displayed in results

**Expected Results**: Topic-based searches return relevant conversations with topic info

**Pass/Fail Criteria**: PASS if topic searches work correctly, FAIL if topics not matched

---

#### FUNC-001.5: Search Edge Cases
**Steps:**
1. Search with empty query string ""
2. Search with very long query (500+ characters)
3. Search with special characters: "python & javascript"
4. Search with non-existent terms: "nonexistentterm12345"
5. Search with only whitespace

**Expected Results**: 
- Empty/whitespace queries handled gracefully
- Long queries don't crash system
- Special characters handled safely
- No results for non-existent terms (not an error)

**Pass/Fail Criteria**: PASS if edge cases handled gracefully, FAIL if crashes or errors

---

## FUNC-002: Add Conversation Testing

**Objective**: Verify conversation storage, indexing, and file organization functionality.

### Test Cases

#### FUNC-002.1: Basic Conversation Addition
**Steps:**
1. Execute add_conversation with:
   - content: "Test conversation about React hooks and state management"
   - title: "React Development Discussion"
   - date: current date
2. Verify success response with file path
3. Check file exists in expected location (year/month folder)
4. Verify content written correctly to file
5. Check index.json updated with new entry

**Expected Results**: Conversation stored correctly with proper file organization

**Pass/Fail Criteria**: PASS if file created and indexed correctly, FAIL if storage issues

---

#### FUNC-002.2: Auto-Topic Extraction
**Steps:**
1. Add conversation with known technical terms:
   - content: "Discussing Docker containers, Kubernetes deployment, and AWS infrastructure"
2. Check extracted topics include: docker, kubernetes, aws
3. Verify topics.json updated with new topic counts
4. Add another conversation with overlapping topics
5. Verify topic counts incremented correctly

**Expected Results**: Topics extracted automatically and tracked properly

**Pass/Fail Criteria**: PASS if topics extracted and counted correctly, FAIL if topic issues

---

#### FUNC-002.3: Date Handling
**Steps:**
1. Add conversation with explicit date: "2024-12-01T10:30:00Z"
2. Verify file placed in correct year/month folder (2024/12-december)
3. Add conversation with invalid date format
4. Verify graceful handling of date errors
5. Add conversation with no date (should use current date)

**Expected Results**: Dates parsed correctly and files organized by date

**Pass/Fail Criteria**: PASS if date handling correct, FAIL if wrong organization or crashes

---

#### FUNC-002.4: File Naming and Organization
**Steps:**
1. Add conversation with title containing special characters: "Test/Title: With Special *Characters*"
2. Verify filename sanitized appropriately
3. Add multiple conversations on same date with different titles
4. Verify unique filenames generated
5. Check directory structure follows year/month pattern

**Expected Results**: File names sanitized and organized logically

**Pass/Fail Criteria**: PASS if naming and organization correct, FAIL if conflicts or bad names

---

#### FUNC-002.5: Large Content Handling
**Steps:**
1. Add conversation with large content (>1MB text)
2. Verify successful storage without truncation
3. Add conversation with very long title (>200 characters)
4. Test content with various character encodings (Unicode, emojis)
5. Verify all content preserved accurately

**Expected Results**: Large and complex content handled correctly

**Pass/Fail Criteria**: PASS if content preserved accurately, FAIL if truncation or encoding issues

---

## FUNC-003: Weekly Summary Testing

**Objective**: Verify weekly summary generation provides accurate analysis and insights.

### Test Data Setup
Create conversations across multiple weeks with varying patterns:

```bash
# Week 1: Programming focus
Week 1 Day 1: "Python function optimization techniques"
Week 1 Day 3: "Database indexing strategies" 
Week 1 Day 5: "Code review best practices"

# Week 2: Infrastructure focus  
Week 2 Day 2: "Docker containerization workflow"
Week 2 Day 4: "Kubernetes cluster setup"
Week 2 Day 6: "AWS deployment automation"

# Current week: Mixed topics
Current Day -2: "React component testing"
Current Day -1: "API design principles"
```

### Test Cases

#### FUNC-003.1: Current Week Summary
**Steps:**
1. Execute generate_weekly_summary() with week_offset=0
2. Verify summary includes only current week's conversations
3. Check date range calculation accuracy
4. Verify conversation count correct
5. Review topics analysis for current week

**Expected Results**: Accurate summary of current week with correct date boundaries

**Pass/Fail Criteria**: PASS if current week summarized correctly, FAIL if wrong timeframe or data

---

#### FUNC-003.2: Historical Week Summary
**Steps:**
1. Execute generate_weekly_summary(week_offset=1) for last week
2. Execute generate_weekly_summary(week_offset=2) for two weeks ago
3. Verify each summary contains only conversations from target week
4. Check date calculations for different week offsets
5. Compare topic distributions across weeks

**Expected Results**: Historical weeks summarized accurately with correct date ranges

**Pass/Fail Criteria**: PASS if historical summaries correct, FAIL if wrong timeframe

---

#### FUNC-003.3: Content Analysis Features
**Steps:**
1. Generate summary for week with known conversation types
2. Verify coding tasks identified correctly
3. Check decisions/recommendations extraction
4. Verify learning topics identification
5. Review topic frequency analysis

**Expected Results**: Content analysis identifies different conversation types accurately

**Pass/Fail Criteria**: PASS if analysis features work correctly, FAIL if poor categorization

---

#### FUNC-003.4: Summary Formatting and Storage
**Steps:**
1. Generate weekly summary and capture output
2. Verify markdown formatting is correct
3. Check that summary file is saved to summaries/weekly/
4. Verify filename format: "week-YYYY-MM-DD.md"
5. Test summary readability and completeness

**Expected Results**: Summaries well-formatted and properly stored

**Pass/Fail Criteria**: PASS if formatting and storage correct, FAIL if format issues

---

#### FUNC-003.5: Empty Week Handling
**Steps:**
1. Generate summary for week with no conversations
2. Verify appropriate "no conversations" message
3. Test with week containing only empty/minimal conversations
4. Check handling of weeks with only error conversations
5. Verify graceful degradation for sparse data

**Expected Results**: Empty or sparse weeks handled gracefully

**Pass/Fail Criteria**: PASS if empty weeks handled well, FAIL if errors or poor messaging

---

## FUNC-004: Data Persistence and Integrity

**Objective**: Verify data persistence, index integrity, and cross-tool functionality.

### Test Cases

#### FUNC-004.1: Index Consistency
**Steps:**
1. Add several conversations via add_conversation
2. Verify each conversation appears in index.json
3. Search for added conversations and verify they're found
4. Check topics.json reflects added conversations
5. Verify index file format is valid JSON

**Expected Results**: Index files remain consistent and valid

**Pass/Fail Criteria**: PASS if indexes consistent, FAIL if corruption or inconsistency

---

#### FUNC-004.2: Cross-Tool Data Flow
**Steps:**
1. Add conversation via add_conversation: "DevOps pipeline automation"
2. Search for "devops" and verify new conversation found
3. Generate weekly summary and verify conversation included
4. Check that all tools see the same data consistently

**Expected Results**: Data flows correctly between all tools

**Pass/Fail Criteria**: PASS if cross-tool consistency maintained, FAIL if data missing

---

#### FUNC-004.3: File System Recovery
**Steps:**
1. Backup current index files
2. Delete index.json file
3. Restart MCP server
4. Verify index file recreated as empty
5. Add new conversation and verify indexing works
6. Restore backup and verify recovery

**Expected Results**: System recovers gracefully from missing index files

**Pass/Fail Criteria**: PASS if recovery successful, FAIL if system cannot recover

---

## FUNC-005: Performance Validation

**Objective**: Verify functional performance meets user expectations.

### Test Cases

#### FUNC-005.1: Search Performance
**Steps:**
1. Create 50+ test conversations
2. Execute searches and measure response times
3. Test with various query lengths and complexities
4. Verify performance doesn't degrade significantly with dataset size

**Performance Targets**:
- Simple search (1-2 words): < 2 seconds
- Complex search (5+ words): < 5 seconds
- Large dataset (100+ conversations): < 10 seconds

**Pass/Fail Criteria**: PASS if performance targets met, FAIL if excessive delays

---

#### FUNC-005.2: Storage Performance  
**Steps:**
1. Add large conversations and measure storage time
2. Test with rapid successive additions
3. Verify index updates don't slow down significantly
4. Monitor file system usage patterns

**Performance Targets**:
- Small conversation (<10KB): < 1 second
- Large conversation (<1MB): < 5 seconds
- Index updates: < 2 seconds

**Pass/Fail Criteria**: PASS if storage performance acceptable, FAIL if slow operations

---

## Test Execution Guidelines

### Pre-Test Setup
1. Backup existing conversation data
2. Clear test data from previous runs
3. Verify MCP server running and connected
4. Prepare test data templates

### Test Data Management
- Use consistent test conversations across test runs
- Document test data used for each test case
- Clean up test data after completion
- Maintain separate test datasets for different test areas

### Result Validation
- Verify both positive and negative test cases
- Check edge cases and boundary conditions
- Validate error handling and recovery
- Confirm performance within acceptable ranges

### Documentation
- Record actual vs. expected results
- Document any deviations or unexpected behavior
- Note performance measurements
- Capture screenshots for UI-related issues

---

**Test Suite Version**: 1.0  
**Last Updated**: 2025-06-01  
**Author**: Functional Test Suite Generator