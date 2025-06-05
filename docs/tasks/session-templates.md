# Session-Based Test Management Templates

## Session Sheet Template

Use this template for each exploratory testing session. Fill out all sections during or immediately after the session.

---

### CHARTER
**Mission Statement:** [Brief description of what you're testing and why]

**Areas to Test:** [Specific product areas, features, or risk areas being explored]

**Duration:** [short/normal/long or actual time]

---

### BASIC SESSION DATA

**Tester:** Adam  
**Date/Time Started:** [YYYY-MM-DD HH:MM]  
**Session ID:** [e.g., CMS-001, CMS-002]  
**Product Version:** [MCP server version/commit hash if available]  
**Test Environment:** [Ubuntu 20.04 WSL, Claude Desktop version]

---

### TASK BREAKDOWN

**Duration:** [Actual session length in minutes]

**Test Design and Execution:** [Percentage of time spent actively testing]  
**Bug Investigation and Reporting:** [Percentage of time spent investigating and documenting issues]  
**Session Setup:** [Percentage of time spent on setup, configuration, note-taking]

**Charter vs. Opportunity:** [% on charter / % on unplanned exploration]

---

### DATA FILES

**Test Data Used:** [List any specific test conversations, queries, or datasets used]  
**Files Created:** [Any new test files, logs, or artifacts created during session]  
**External Resources:** [Documentation, tools, or references consulted]

---

### TEST NOTES

[Detailed notes about what you tested and how. Include:]
- **Coverage:** What areas/features you explored
- **Oracles:** How you determined if something was working correctly
- **Activity:** Specific actions taken, tests performed
- **Observations:** What you noticed, both expected and unexpected
- **Patterns:** Any interesting behaviors or recurring issues

#### Test Strategy Applied:
- [ ] Function Testing (testing what it can do)
- [ ] Domain Testing (boundary values, data partitioning) 
- [ ] Stress Testing (overloading the system)
- [ ] Flow Testing (sequences of operations)
- [ ] Scenario Testing (realistic user stories)
- [ ] Claims Testing (verifying stated requirements)
- [ ] User Testing (realistic usage patterns)
- [ ] Risk Testing (exploring specific risk areas)

---

### BUGS

**Bug #1:** [Brief headline description]  
**Details:** [Steps to reproduce, expected vs. actual results, severity assessment]

**Bug #2:** [Brief headline description]  
**Details:** [Steps to reproduce, expected vs. actual results, severity assessment]

[Continue for additional bugs found]

---

### ISSUES

**Issue #1:** [Non-bug problems that impacted testing]  
**Details:** [Description of testing obstacles, questions raised, blockers encountered]

**Issue #2:** [Additional issues]  
**Details:** [Continue as needed]

---

### SESSION SUMMARY

**Charter Completion:** [Was the charter fulfilled? If not, what remains?]  
**Key Findings:** [Most important discoveries from this session]  
**Confidence Level:** [How confident are you in the tested areas?]  
**Follow-up Needed:** [What should be tested next? Any specific areas needing attention?]

---

## Session Debrief Checklist

Use this checklist during session debriefing (can be self-debrief if testing alone).

### Charter Validation
- [ ] Does the charter text match the bulk of testing actually done?
- [ ] Was the charter fulfilled during the session?
- [ ] If charter was not completed, is remaining work documented?
- [ ] If charter was changed during session, is the change documented?

### Session Data Quality
- [ ] Duration is reasonably accurate (within 20%)?
- [ ] Time percentages add up to 100% and feel correct?
- [ ] Test execution time relates to work that could discover bugs?
- [ ] Bug investigation time relates only to bug work that interrupted testing?
- [ ] Setup time covers session-related admin work?

### Test Coverage and Notes
- [ ] Test notes are comprehensible (will make sense in 3 months)?
- [ ] Notes answer "what happened in this session?"
- [ ] Coverage, oracles, and activities are documented?
- [ ] Any test data or artifacts are properly saved/referenced?

### Bug and Issue Reporting
- [ ] All bugs have clear headlines and sufficient detail?
- [ ] Formal bug reports written where applicable?
- [ ] Issues (testing obstacles) documented separately from bugs?
- [ ] If no issues found, was session really obstacle-free?

### Session Integrity
- [ ] Does this report faithfully represent the testing that was done?
- [ ] Are there follow-up sessions needed based on this work?
- [ ] Should this session be extended or amended?
- [ ] Is the documentation proportionate to the value of the testing?

---

## PROOF Debrief Agenda

Use this structure for session debriefing discussions:

### **Past** - What happened during the session?
- Review charter and actual work performed
- Discuss any charter changes or diversions
- Confirm time allocation accuracy

### **Results** - What was achieved during the session?
- Key findings and discoveries
- Bugs found and their significance
- Test coverage accomplished
- Confidence gained in tested areas

### **Obstacles** - What got in the way of good testing?
- Technical issues or blockers
- Missing information or unclear requirements
- Tool or environment problems
- Time constraints or interruptions

### **Outlook** - What still needs to be done?
- Remaining charter work
- Follow-up sessions needed
- Areas requiring deeper exploration
- Dependencies on other work

### **Feelings** - How does the tester feel about all this?
- Confidence in the testing performed
- Satisfaction with session productivity
- Concerns about untested areas
- Motivation for continuing the work

---

## Session Management Guidelines

### Session Scope
- Keep sessions focused on a single charter/mission
- Target 60-90 minutes for normal sessions
- Allow for shorter (45 min) or longer (2 hour) sessions as needed
- Take breaks if sessions extend beyond 2 hours

### Documentation Efficiency
- Take notes during testing, not just at the end
- Use bullet points and abbreviations during active testing
- Expand notes immediately after session while fresh
- Don't let documentation slow down discovery

### Charter Flexibility
- It's okay to deviate from charter if interesting bugs found
- Document deviations rather than forcing artificial compliance
- Consider changing charter to match actual work performed
- Create new charters for interesting areas discovered

### Bug Reporting Standards
- Report bugs immediately if they're blocking further testing
- For non-blocking bugs, continue testing and document afterward
- Focus on clear reproduction steps and business impact
- Use appropriate severity assessment based on risk analysis

### Session Evaluation
- Aim for high percentage of test execution time
- Minimize setup time through better preparation
- If bug investigation dominates, consider shorter sessions
- Balance chartered work with opportunity testing (80/20 typical)

---

**Template Version**: 1.0  
**Based on**: Session-Based Test Management methodology by James Bach and Jonathan Bach  
**Last Updated**: 2025-06-01