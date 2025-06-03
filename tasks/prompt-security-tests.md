# Prompt: Security Test Suite Generation

## Purpose
Generate comprehensive structured security test procedures to identify vulnerabilities and protect against security threats in software systems.

## Instructions
You are a security testing expert familiar with common vulnerability patterns, threat modeling, and security testing methodologies. Create systematic test procedures that validate security controls and identify potential weaknesses.

### Required Inputs
Before generating security tests, gather this information:
1. **System Architecture** - Application type, technology stack, deployment model
2. **Security Requirements** - Specific security concerns, compliance needs, threat model
3. **Data Sensitivity** - Types of data handled, privacy requirements, exposure risks
4. **Attack Surface** - Input points, interfaces, external dependencies
5. **Security Controls** - Authentication, authorization, encryption, validation mechanisms
6. **Environment** - Production vs. test environments, access controls, monitoring

### Security Test Categories

#### 1. Input Validation & Injection Testing
Test system's resistance to malicious input:

**Injection Attack Testing:**
- SQL injection (if database-driven)
- Command injection (if system calls involved)
- Path traversal/directory traversal
- JSON/XML injection
- Code injection (if applicable)

**Input Validation Testing:**
- Boundary value testing for all inputs
- Special character handling
- Unicode and encoding attacks
- Oversized input handling
- Null/empty input validation

#### 2. Authentication & Authorization Testing
Verify access control mechanisms:

**Authentication Testing:**
- Password/credential validation
- Multi-factor authentication (if implemented)
- Account lockout mechanisms
- Session management
- Password policy enforcement

**Authorization Testing:**
- Role-based access control
- Privilege escalation attempts
- Resource access validation
- Cross-user data access
- Administrative function protection

#### 3. Data Protection & Privacy Testing
Ensure sensitive data is properly protected:

**Data Exposure Testing:**
- Information disclosure in error messages
- Sensitive data in logs or temporary files
- Data transmission security
- Data storage protection
- Backup and recovery security

**Privacy Testing:**
- Personal data handling
- Data retention policies
- Consent mechanisms (if applicable)
- Data anonymization/pseudonymization
- Right to deletion compliance

#### 4. Session & State Management Testing
Validate session security:

**Session Security:**
- Session token generation and randomness
- Session timeout and invalidation
- Session fixation resistance
- Cross-site request forgery (CSRF) protection
- Session hijacking resistance

**State Management:**
- Application state integrity
- Race condition resistance
- Concurrent session handling
- State persistence security

#### 5. Communication Security Testing
Test secure communication mechanisms:

**Network Security:**
- Encryption in transit (TLS/SSL)
- Certificate validation
- Protocol downgrade resistance
- Man-in-the-middle protection

**API Security (if applicable):**
- API authentication and authorization
- Rate limiting and abuse protection
- Input validation for API endpoints
- Response data filtering

### Test Case Structure
For each test case, provide:

#### Test Case Header
- **Test ID** - Unique identifier (SEC-001, SEC-002, etc.)
- **Test Category** - Security area being tested
- **Objective** - What vulnerability/control is being validated
- **Priority** - Critical/High/Medium/Low based on risk

#### Test Procedure
- **Pre-conditions** - Required setup, test data, environment state
- **Test Steps** - Numbered, specific actions to perform
- **Expected Results** - What should happen (secure behavior)
- **Pass/Fail Criteria** - Clear criteria for test evaluation

#### Security Considerations
- **Attack Vector** - How this vulnerability could be exploited
- **Impact Assessment** - Potential damage if vulnerability exists
- **Risk Classification** - Severity level of potential vulnerability

### Test Environment Considerations

#### Test Data Security
- Use sanitized/synthetic test data when possible
- Protect any real data used in testing
- Ensure test data doesn't contain production secrets
- Clean up test data after testing

#### Environment Isolation
- Test in isolated environment when possible
- Avoid testing destructive scenarios in production
- Protect test environment from unauthorized access
- Monitor test activities for security events

#### Tool and Technique Selection
- Use appropriate security testing tools
- Combine automated and manual testing approaches
- Consider both black-box and white-box testing techniques
- Document tools and techniques used

### Common Security Testing Patterns

#### File System Security
- Path traversal attempts
- File permission validation
- Temporary file security
- Configuration file protection

#### Error Handling Security
- Information disclosure in error messages
- Error logging security
- Exception handling robustness
- Graceful failure behavior

#### Resource Protection
- Denial of service resistance
- Resource exhaustion protection
- Rate limiting effectiveness
- Concurrent access handling

#### Configuration Security
- Secure default configurations
- Configuration change validation
- Credential storage security
- Service hardening verification

### Risk-Based Test Prioritization

#### Critical Priority Tests
- Tests for vulnerabilities that could lead to:
  - Data breaches or exposure
  - System compromise
  - Financial loss
  - Regulatory compliance violations

#### High Priority Tests
- Tests for vulnerabilities that could cause:
  - Service disruption
  - Unauthorized access
  - Data integrity issues
  - Reputation damage

#### Medium/Low Priority Tests
- Tests for less severe security issues:
  - Information disclosure
  - Minor access control issues
  - Configuration weaknesses
  - Security hardening opportunities

### Documentation Requirements

#### Test Results Documentation
- Clear pass/fail results for each test
- Evidence of testing performed (screenshots, logs)
- Detailed findings for any failures
- Risk assessment for identified issues

#### Vulnerability Reporting
- Clear vulnerability descriptions
- Reproduction steps for security issues
- Impact assessment and risk rating
- Recommended remediation actions

### Compliance Considerations
Adapt tests based on applicable standards:
- **OWASP Top 10** - Web application security risks
- **ISO 27001** - Information security management
- **NIST Cybersecurity Framework** - Security controls
- **Industry-specific standards** - HIPAA, PCI-DSS, SOX, etc.

### Reference Materials
Base tests on established security frameworks:
- OWASP Testing Guide
- NIST Special Publications (800 series)
- Common Weakness Enumeration (CWE)
- Common Vulnerabilities and Exposures (CVE)

### Output Format
Generate structured test suite including:
- Test categories organized by security domain
- Individual test cases with clear procedures
- Risk-based prioritization
- Environment setup and execution guidance
- Result documentation templates

## Example Usage
```
Create security test suite for:
- System Type: [Web app/API/Desktop/Mobile/System service]
- Technology Stack: [Languages, frameworks, databases]
- Security Concerns: [Data protection/Access control/Communication security]
- Compliance Requirements: [Any specific standards or regulations]
- Testing Environment: [Constraints and considerations]
```

## Key Success Factors
- Tests systematically cover major security vulnerability categories
- Test procedures are specific and executable
- Risk-based prioritization focuses effort on highest threats
- Tests appropriate for technology stack and architecture
- Documentation supports clear security assessment
- Tests can be executed safely without causing damage