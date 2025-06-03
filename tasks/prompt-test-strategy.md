# Prompt: Test Strategy Generation

## Purpose
Generate a comprehensive, risk-based test strategy using the Heuristic Test Strategy Model (HTSM) and Session-Based Test Management (SBTM) methodologies.

## Instructions
You are an expert test strategist familiar with James Bach's Rapid Software Testing methodology, the Heuristic Test Strategy Model, and Session-Based Test Management. Create a test strategy document that follows these principles:

### Required Inputs
Before generating the strategy, gather this information:
1. **Product/System Description** - What is being tested and its primary purpose
2. **Quality Criteria Priorities** - Which quality criteria are most important (Capability, Reliability, Usability, Performance, Security, Compatibility, etc.)
3. **Target User/Tester Profile** - Who will be doing the testing and their skill level
4. **Time Constraints** - Available testing effort and schedule
5. **Business Context** - Risk tolerance, stakes, and success criteria

### Document Structure
Generate a test strategy document with these sections:

#### 1. Overview
- Brief product description and testing mission
- Key stakeholders and their concerns
- Testing approach and methodology

#### 2. Risk Assessment & Test Focus
Use HTSM Quality Criteria Categories to analyze risks:
- **HIGH PRIORITY RISKS** - Critical business/technical risks requiring deep testing
- **MEDIUM PRIORITY RISKS** - Important areas needing solid coverage  
- **LOWER PRIORITY RISKS** - Areas with acceptable risk levels

For each risk area, include:
- Specific risk description
- Business impact if risk materializes
- Testing approach to mitigate risk

#### 3. Test Strategy
- **Testing Approach** - Exploratory vs scripted, risk-based prioritization
- **Product Elements Coverage** - Structure, Functions, Data, Interfaces, Platform, Operations, Time
- **Test Techniques** - Which general test techniques will be applied (Function, Domain, Stress, Flow, Scenario, Claims, User, Risk testing)
- **Test Environment** - Setup requirements and constraints

#### 4. Deliverables
- Session reports and documentation approach
- Bug reporting standards and severity criteria
- Test artifacts and evidence to be produced
- Success criteria and go/no-go decision points

#### 5. Test Sessions Overview
- List of proposed test sessions with duration and priority
- Brief description of each session's charter
- Total estimated effort

### Key Principles to Follow
- **Risk-based prioritization** - Focus most effort on highest impact/likelihood risks
- **Context-driven approach** - Adapt strategy to specific project constraints
- **Rapid testing principles** - Emphasize skilled testers over rigid processes
- **Session-based structure** - Organize work into focused, time-boxed sessions
- **Pragmatic scope** - Match testing investment to business needs

### Reference Materials
Use these documents as methodology references:
- Heuristic Test Strategy Model (HTSM) by James Bach
- Session-Based Test Management methodology
- Rapid Software Testing principles
- Test Plan Evaluation Model heuristics

### Output Format
- Markdown document with clear headings and structure
- Include risk analysis matrix or prioritized lists
- Provide actionable session recommendations
- Keep strategy concise but comprehensive (3-5 pages typical)

## Example Usage
```
Create a test strategy for [PRODUCT NAME]:
- Product: [Brief description of what's being tested]
- Top Quality Concerns: [Security, Performance, Usability, etc.]
- Tester Profile: [Experience level and role]
- Time Available: [Hours/days available for testing]
- Business Context: [Stakes, deadlines, risk tolerance]
```

## Key Success Factors
- Strategy clearly prioritizes testing effort based on risk
- Sessions are focused and executable within stated time constraints
- Testing approach matches tester capabilities and project constraints
- Risk analysis drives all testing decisions
- Document serves as practical guide for test execution