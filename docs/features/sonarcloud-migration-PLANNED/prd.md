# Product Requirements Document: SonarCloud Migration

## Introduction/Overview

Migrate the Claude Memory MCP project from self-hosted SonarQube (Community Edition at `44.206.255.230:9000`) to SonarCloud's cloud-hosted platform. This migration enables public dashboard visibility for recruiters and peers while reducing infrastructure maintenance for this public repository.

**Problem Statement**: The current self-hosted SonarQube instance requires manual infrastructure management and is not publicly accessible without exposing the IP address. For public repositories, SonarCloud provides better visibility, automatic PR decoration, and zero maintenance overhead.

## Goals

**Primary Goals:**
1. Enable public access to quality metrics dashboard for portfolio/recruitment visibility
2. Maintain continuous code quality analysis with existing standards
3. Reduce infrastructure maintenance for public repository quality checks
4. Improve GitHub integration with automatic badges and PR decoration

**Secondary Goals:**
1. Preserve historical quality data and trends from self-hosted instance
2. Establish reusable migration pattern for other public repositories
3. Close obsolete infrastructure issues (Issue #10 - domain migration)

## User Stories

**As a recruiter/hiring manager**, I want to:
- View live code quality metrics on the repository README
- Access the public SonarCloud dashboard to assess code quality
- See quality gate status on pull requests

**As a developer/peer**, I want to:
- Quickly verify code quality standards are maintained
- See quality metrics without requiring access credentials
- Trust that CI/CD blocks merges on quality gate failures

**As a repository maintainer**, I want to:
- Eliminate manual SonarQube server maintenance for public repos
- Automatically display quality badges in README
- Preserve existing quality standards and thresholds
- Keep self-hosted instance available for private projects

## Functional Requirements

### FR1: SonarCloud Account Setup
- Create/configure SonarCloud account linked to GitHub
- Import `claude-memory-mcp` project to SonarCloud
- Configure project key and organization settings
- Generate SonarCloud authentication token for GitHub Actions

### FR2: Quality Gate Configuration
- Use SonarCloud default quality gate (or verify custom gate compatibility)
- Ensure quality gate passes with current codebase
- Configure thresholds equivalent to current self-hosted setup:
  - New Code: 0 issues
  - Security Hotspots: 100% reviewed
  - Coverage: ≥0% (or project-specific threshold)
  - Duplicated Lines: ≤25%

### FR3: CI/CD Pipeline Update
- Replace self-hosted SonarQube action with SonarCloud action in `.github/workflows/build.yml`
- Update secrets in GitHub repository (`SONAR_TOKEN`, remove old credentials)
- Maintain existing 3-stage pipeline structure (quick-checks → tests+sonarcloud → review)
- Ensure quality gate failures block PR merges

### FR4: Public Visibility Features
- Add SonarCloud quality gate badge to `README.md`
- Add direct link to SonarCloud dashboard in `README.md`
- Verify badge updates automatically on quality changes

### FR5: Historical Data Preservation
- Export or document current quality metrics from self-hosted instance
- Capture baseline metrics (coverage %, issues, security hotspots, etc.)
- Store historical data reference in `docs/` for future comparison

### FR6: Cleanup and Issue Management
- Close Issue #10 ("Replace IP-based SonarQube URL with domain name") as won't fix
- Close Issue #9 ("SonarQube: Support HTTPS") if no longer relevant
- Update documentation to reference SonarCloud instead of self-hosted instance

## Non-Goals (Out of Scope)

1. **Self-Hosted Decommission**: Keep self-hosted SonarQube running for private projects
2. **Quality Standards Changes**: Maintain existing quality gate thresholds (no relaxation)
3. **Code Changes**: No application code modifications required
4. **Private Repository Migration**: Only migrate public `claude-memory-mcp` repo (establish pattern for later)
5. **SonarCloud Premium Features**: Use free tier for public repositories only

## Technical Considerations

### GitHub Actions Workflow Update
Current workflow uses `SonarSource/sonarqube-scan-action@v5` (or v6) pointing to self-hosted instance. Update to:

```yaml
- name: SonarCloud Scan
  uses: SonarSource/sonarcloud-github-action@master
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### Required Secrets
- **New**: `SONAR_TOKEN` - SonarCloud authentication token (GitHub repository secret)
- **Remove**: Self-hosted SonarQube credentials (if stored as secrets)

### Quality Gate Compatibility
Current custom quality gate:
- Issues > 0 (new code)
- Security Hotspots Reviewed < 100%
- Coverage < 0.0%
- Duplicated Lines > 25.0%

**Decision**: Use SonarCloud default quality gate if it passes; otherwise configure custom gate.

### Project Key
Use consistent project key format: `adamkwhite_claude-memory-mcp` (GitHub organization + repo name)

## Success Metrics

1. **Migration Success**:
   - [ ] SonarCloud project created and linked to GitHub
   - [ ] CI/CD pipeline runs successfully with SonarCloud
   - [ ] Quality gate passes on main branch

2. **Visibility Success**:
   - [ ] Quality gate badge visible in README
   - [ ] Public dashboard accessible without authentication
   - [ ] Badge updates automatically on code changes

3. **Maintenance Reduction**:
   - [ ] No self-hosted instance configuration required for this repo
   - [ ] CI/CD pipeline runs without manual intervention
   - [ ] Quality gate failures block merges as expected

4. **Data Preservation**:
   - [ ] Historical metrics documented before migration
   - [ ] Baseline comparison available for validation

## Open Questions

1. **Migration Pattern**: Should we document the migration steps for reuse with other public repos?
2. **Badge Placement**: Where in README should the quality badge appear? (Header, badges section, status section?)
3. **Historical Data**: What format should we use to preserve historical metrics? (Markdown doc, CSV, screenshots?)

## Related Work

- **Issue #56**: Setup SonarCloud and import project
- **Issue #57**: Update CI/CD pipeline to use SonarCloud
- **Issue #58**: Add README badges and visibility features
- **Issue #59**: Verification and cleanup tasks

## References

- Self-hosted SonarQube: http://44.206.255.230:9000/dashboard?id=Claude-MCP
- GitHub Repository: https://github.com/adamkwhite/claude-memory-mcp
- GitHub Issues: [#56](https://github.com/adamkwhite/claude-memory-mcp/issues/56), [#57](https://github.com/adamkwhite/claude-memory-mcp/issues/57), [#58](https://github.com/adamkwhite/claude-memory-mcp/issues/58), [#59](https://github.com/adamkwhite/claude-memory-mcp/issues/59)
- Related Issues: #10 (domain migration - to be closed), #9 (HTTPS support - to be evaluated)
