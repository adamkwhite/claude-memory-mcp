# Reusable Testing Prompt Library

## Overview

This library contains 7 reusable prompts for generating comprehensive testing documentation based on established testing methodologies including Heuristic Test Strategy Model (HTSM), Session-Based Test Management (SBTM), and Rapid Software Testing (RST).

## Prompt Collection

### 📋 Strategic Planning Prompts

#### 1. `prompt-test-strategy.md`
**Purpose:** Generate risk-based test strategies using HTSM methodology  
**Output:** Comprehensive test strategy with risk analysis, priorities, and session planning  
**Use When:** Starting a new testing effort, need strategic direction, risk assessment required

#### 2. `prompt-test-execution-guide.md`  
**Purpose:** Create practical execution guides for managing testing activities  
**Output:** Phase-based execution plan with resource management and progress tracking  
**Use When:** Need structured approach to execute testing, team coordination required

### 🎯 Exploratory Testing Prompts

#### 3. `prompt-session-charters.md`
**Purpose:** Generate focused session charters for exploratory testing  
**Output:** Time-boxed session charters with clear missions and risk focus  
**Use When:** Planning exploratory testing, need focused test sessions, SBTM approach

#### 4. `prompt-session-templates.md`
**Purpose:** Create SBTM documentation templates for session recording  
**Output:** Session sheets, debrief checklists, and management templates  
**Use When:** Implementing SBTM, need consistent documentation, session quality control

### 🔧 Structured Testing Prompts

#### 5. `prompt-security-tests.md`
**Purpose:** Generate systematic security test procedures  
**Output:** Structured security test cases covering major vulnerability categories  
**Use When:** Security testing required, need systematic coverage, compliance validation

#### 6. `prompt-integration-tests.md`
**Purpose:** Create integration and compatibility test suites  
**Output:** Protocol compliance, API testing, and compatibility validation procedures  
**Use When:** Testing system interactions, API validation, compatibility requirements

#### 7. `prompt-functional-tests.md`
**Purpose:** Generate comprehensive functional test procedures  
**Output:** Requirement validation tests covering core functionality  
**Use When:** Functional validation needed, requirement verification, acceptance testing

## Usage Patterns

### 🚀 Complete Testing Program
For comprehensive testing of a new system:

1. **Start with Strategy:** Use `prompt-test-strategy.md` to establish overall approach
2. **Plan Execution:** Use `prompt-test-execution-guide.md` to organize testing phases
3. **Create Sessions:** Use `prompt-session-charters.md` for exploratory testing
4. **Setup Documentation:** Use `prompt-session-templates.md` for consistent recording
5. **Add Structured Tests:** Use specific test suite prompts as needed

### ⚡ Quick Focused Testing
For targeted testing of specific areas:

1. **Security Focus:** Use `prompt-security-tests.md` for security validation
2. **Integration Focus:** Use `prompt-integration-tests.md` for system interactions
3. **Functional Focus:** Use `prompt-functional-tests.md` for feature validation
4. **Add Sessions:** Use `prompt-session-charters.md` for exploratory coverage

### 🔄 Agile/Continuous Testing
For ongoing testing in agile environments:

1. **Sprint Planning:** Use `prompt-session-charters.md` for sprint-focused sessions
2. **Risk Assessment:** Use `prompt-test-strategy.md` for periodic risk review
3. **Targeted Testing:** Use specific test suite prompts for regression areas
4. **Session Management:** Use `prompt-session-templates.md` for daily execution

## Prompt Customization

### Input Parameters
Each prompt accepts these types of inputs:
- **System/Product Description** - What's being tested
- **Quality Priorities** - Most important quality criteria
- **Resource Constraints** - Team, time, environment limitations
- **Risk Assessment** - Known or suspected high-risk areas
- **Context Factors** - Compliance, stakeholders, methodology

### Output Adaptation
Prompts generate documentation that can be:
- **Scaled** - From solo testing to large teams
- **Formalized** - From agile to regulated environments
- **Specialized** - For specific domains or technologies
- **Integrated** - Combined with existing processes

### Methodology Integration
Prompts are based on these methodologies:
- **HTSM** - Heuristic Test Strategy Model for risk-based planning
- **SBTM** - Session-Based Test Management for exploratory testing
- **RST** - Rapid Software Testing principles for skilled testing
- **Context-Driven** - Adapting approach to specific project needs

## Best Practices

### Prompt Usage
- **Provide Complete Context** - Give detailed system and requirement information
- **Specify Constraints** - Include time, resource, and skill limitations
- **Identify Priorities** - Clearly state most important quality criteria
- **Request Specific Outputs** - Ask for particular formats or detail levels

### Document Integration
- **Start Strategic** - Begin with strategy before detailed procedures
- **Layer Approaches** - Combine exploratory and structured testing
- **Maintain Traceability** - Link session charters to strategic priorities
- **Iterate and Improve** - Refine based on execution experience

### Quality Assurance
- **Review Generated Content** - Validate against actual project needs
- **Customize for Context** - Adapt to specific technologies and constraints
- **Validate with Team** - Ensure approaches match team capabilities
- **Update Based on Learning** - Refine prompts based on results

## Example Workflows

### New Project Testing Setup
```
1. Use prompt-test-strategy.md with:
   - Product: [Your system description]
   - Priorities: [Security, Performance, etc.]
   - Resources: [Team size, timeline]
   
2. Use prompt-session-charters.md with:
   - Risk areas from strategy
   - Available session time
   - Tester skill levels
   
3. Use specific test suite prompts as needed
4. Use prompt-execution-guide.md to coordinate
```

### Security-Focused Testing
```
1. Use prompt-security-tests.md with:
   - System architecture details
   - Security requirements
   - Compliance needs
   
2. Use prompt-session-charters.md for:
   - Exploratory security testing
   - Risk-based session planning
   
3. Use prompt-test-execution-guide.md for:
   - Coordinating security testing phases
```

### API Testing Program
```
1. Use prompt-integration-tests.md with:
   - API specifications
   - Protocol requirements
   - Client compatibility needs
   
2. Use prompt-functional-tests.md for:
   - API functionality validation
   - Business logic testing
   
3. Add exploratory sessions for edge cases
```

## Methodology References

### Core Testing Methodologies
- **James Bach & Michael Bolton** - Rapid Software Testing
- **James Bach** - Heuristic Test Strategy Model
- **James & Jonathan Bach** - Session-Based Test Management
- **Context-Driven Testing Community** - Context-driven principles

### Supporting Frameworks
- **OWASP** - Security testing guidance
- **IEEE 829** - Test documentation standards
- **ISO/IEC 29119** - Software testing standards
- **Agile Testing** - Continuous testing practices

## Getting Started

1. **Choose Your Starting Point** - Strategy for new projects, specific prompts for targeted needs
2. **Gather Required Information** - System details, constraints, priorities
3. **Generate Initial Documentation** - Use appropriate prompts with your context
4. **Customize and Refine** - Adapt generated content to your specific needs
5. **Execute and Improve** - Use the documentation and refine based on experience

---

**Library Version:** 1.0  
**Based on:** HTSM, SBTM, and RST methodologies  
**Last Updated:** 2025-06-01  
**Usage:** Provide context-specific inputs to generate tailored testing documentation