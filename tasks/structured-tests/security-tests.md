# Security Test Suite: Claude Conversation Memory MCP Server

## Test Suite Overview
This suite contains structured test procedures focused on security vulnerabilities and data protection. Execute these tests in a controlled environment to verify the system's security posture.

---

## SEC-001: File Path Injection Testing

**Objective**: Verify the system prevents directory traversal and file path injection attacks.

### Test Data Setup
```bash
# Create test directory structure
mkdir -p /tmp/security-test
echo "SENSITIVE_DATA" > /tmp/security-test/sensitive.txt
echo "SYSTEM_FILE" > /etc/security-test-target.txt  # If permissions allow
```

### Test Cases

#### SEC-001.1: Basic Directory Traversal
**Steps:**
1. Start MCP server and connect via Claude Desktop
2. Execute `add_conversation` with malicious file path
   - Content: "Test conversation"
   - Title: "../../../tmp/security-test/malicious"
3. Check if file was created outside storage directory
4. Verify no sensitive file access occurred

**Expected Result**: File created only within storage directory, no access to /tmp/security-test/

**Pass/Fail Criteria**: PASS if confined to storage dir, FAIL if file created elsewhere

---

#### SEC-001.2: Absolute Path Injection  
**Steps:**
1. Execute `add_conversation` with absolute path
   - Content: "Test conversation"
   - Title: "/tmp/security-test/absolute-path-test"
2. Check file system for unauthorized file creation
3. Verify error handling doesn't expose system information

**Expected Result**: Operation contained within storage directory

**Pass/Fail Criteria**: PASS if no file outside storage, FAIL if system access

---

#### SEC-001.3: Windows Path Injection (WSL Context)
**Steps:**
1. Execute `add_conversation` with Windows-style paths
   - Content: "Test conversation" 
   - Title: "C:\\Windows\\System32\\test"
2. Execute with UNC paths
   - Title: "\\\\server\\share\\test"
3. Verify path handling and normalization

**Expected Result**: Paths normalized and contained within storage

**Pass/Fail Criteria**: PASS if paths safely handled, FAIL if external access

---

## SEC-002: Data Exposure Testing

**Objective**: Ensure personal conversation data is not exposed through logs, errors, or temporary files.

### Test Cases

#### SEC-002.1: Error Message Data Exposure
**Steps:**
1. Create conversation with sensitive content: "My password is 123456789"
2. Trigger error conditions:
   - Invalid date format
   - Corrupt JSON in index
   - Permission denied on storage directory
3. Examine all error messages and logs
4. Search for sensitive data fragments

**Expected Result**: No sensitive conversation content in error messages

**Pass/Fail Criteria**: PASS if no sensitive data exposed, FAIL if data found in errors

---

#### SEC-002.2: Log File Analysis
**Steps:**
1. Enable verbose logging if available
2. Perform normal operations with sensitive test data
3. Review server logs and application logs
4. Search for conversation content, file paths, personal data

**Expected Result**: Logs contain only operational information, no conversation content

**Pass/Fail Criteria**: PASS if no content logged, FAIL if conversation data in logs

---

#### SEC-002.3: Temporary File Security
**Steps:**
1. Monitor /tmp and system temp directories during operations
2. Execute search operations with large result sets
3. Execute weekly summary generation
4. Check for temporary files containing conversation data
5. Verify temporary files are cleaned up

**Expected Result**: No temporary files with conversation content

**Pass/Fail Criteria**: PASS if no temp files or cleaned up, FAIL if data persists

---

## SEC-003: JSON Injection Testing

**Objective**: Verify the system safely handles malformed JSON and injection attempts.

### Test Cases  

#### SEC-003.1: Malformed JSON in Content
**Steps:**
1. Execute `add_conversation` with JSON-breaking content:
   ```
   Content: 'Test with "quotes" and \backslashes and {"json": "objects"}'
   ```
2. Execute with control characters: newlines, tabs, null bytes
3. Verify conversation storage and index integrity
4. Confirm search functionality still works

**Expected Result**: Content properly escaped and stored safely

**Pass/Fail Criteria**: PASS if handled safely, FAIL if JSON corruption or parsing errors

---

#### SEC-003.2: Index File Corruption Resistance
**Steps:**
1. Backup current index.json
2. Execute `add_conversation` with content designed to break JSON parsing
3. Verify index.json remains valid JSON
4. Test search functionality continues working
5. Restore backup if needed

**Expected Result**: Index files remain valid and functional

**Pass/Fail Criteria**: PASS if index integrity maintained, FAIL if corruption occurs

---

## SEC-004: File Permission Testing

**Objective**: Verify proper file permissions and access controls on stored data.

### Test Cases

#### SEC-004.1: Storage Directory Permissions
**Steps:**
1. Check permissions on ~/claude-memory directory
2. Check permissions on conversation files
3. Check permissions on index files
4. Verify files are not world-readable

**Commands:**
```bash
ls -la ~/claude-memory/
ls -la ~/claude-memory/conversations/
find ~/claude-memory -type f -exec ls -l {} \;
```

**Expected Result**: Files readable only by owner, not world-accessible

**Pass/Fail Criteria**: PASS if permissions restrictive, FAIL if world-readable

---

#### SEC-004.2: File Creation Permissions
**Steps:**
1. Add new conversation via MCP
2. Check permissions on newly created files
3. Verify subdirectories have correct permissions
4. Test with umask modifications

**Expected Result**: New files inherit secure permissions

**Pass/Fail Criteria**: PASS if secure permissions, FAIL if overly permissive

---

## SEC-005: Input Validation Testing

**Objective**: Verify robust input validation prevents malicious input processing.

### Test Cases

#### SEC-005.1: Oversized Input Handling
**Steps:**
1. Create very large conversation content (>10MB)
2. Execute `add_conversation` with oversized input
3. Execute search with very long query strings
4. Monitor memory usage and system response

**Expected Result**: System handles large inputs gracefully or rejects appropriately

**Pass/Fail Criteria**: PASS if handled safely, FAIL if crash or resource exhaustion

---

#### SEC-005.2: Special Character Handling
**Steps:**
1. Test with Unicode content, emojis, special characters
2. Test with binary data patterns
3. Test with script injection attempts in titles
4. Verify proper encoding/decoding

**Expected Result**: All input handled safely with proper encoding

**Pass/Fail Criteria**: PASS if safe handling, FAIL if processing errors or injection

---

## Test Execution Guidelines

### Pre-Test Setup
1. Backup current conversation data
2. Prepare isolated test environment  
3. Enable any available logging/monitoring
4. Document system state before testing

### During Testing
1. Document all steps and observations
2. Capture screenshots of error messages
3. Save copies of any suspicious files or outputs
4. Note performance impacts

### Post-Test Cleanup
1. Remove any test files created outside storage
2. Restore backups if needed
3. Reset file permissions if modified
4. Document findings and recommendations

### Risk Classification
- **Critical**: Data exposure, system access, data loss
- **High**: Predictable vulnerabilities, weak access controls  
- **Medium**: Information disclosure, input validation gaps
- **Low**: Minor security improvements, hardening opportunities

---

**Test Suite Version**: 1.0  
**Last Updated**: 2025-06-01  
**Author**: Security Test Suite Generator