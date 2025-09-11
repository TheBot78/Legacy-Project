# GeneWeb Migration – QA Test Strategy

## Amendment History
| Version | Date       | Author           | Description                      |
|---------|------------|-----------------|----------------------------------|
| 0.1     | 2025-09-08 | QA Team (Draft) | Initial draft of QA strategy      |
| 0.2     | 2025-09-11 | QA Team         | Expanded with Golden Master & TDD |

## Reviewers
- QA Lead  
- Project Manager  
- Development Team Lead  

## Approvals
- CoinLegacy Inc. Project Sponsor  
- Technical Lead  

## Distributions
- QA Team  
- Development Team  
- Project Stakeholders  

## Document Status
This is a controlled document.

Whilst this document may be printed, the electronic version should be a controlled document located in an agreed document store. Any printed copies of this document are not controlled.

## Related Documents
- [GeneWeb Repository](https://github.com/geneweb/geneweb)  
- CoinLegacy Project Brief (*G-ING-900_legacy.pdf*)  
- QA Strategy Reference (Testlio, 2023)  

## Glossary of Terms
- **Golden Master**: Characterization testing technique to capture and lock legacy outputs.  
- **TDD**: Test-Driven Development.  
- **CI/CD**: Continuous Integration and Continuous Deployment.  
- **PEP8**: Python coding style guide.  
- **WCAG**: Web Content Accessibility Guidelines.  

---

# 1. Introduction

## 1.1 Objectives
- Preserve the functional behavior of legacy OCaml code during migration.  
- Provide a secure, maintainable Python service around GeneWeb.  
- Ensure QA coverage across unit, integration, performance, and security levels.  

## 1.2 Scope
- Testing Python service (FastAPI) interfacing with GeneWeb.  
- Validation of key endpoints: `/health`, `/api/person/{id}`, basic HTML UI.  
- Security, accessibility, and compliance with GDPR.  

---

# 2. Testing Overview

## 2.1 Test Lifecycle
- Shift-left testing, integrated from Day 0.  
- TDD for new features.  
- Regression via Golden Master.  
- CI/CD pipeline with automated checks.  

## 2.2 Test Approach
- **Golden Master** for legacy protection.  
- **Unit & Integration tests** via pytest.  
- **E2E tests** simulating user workflows.  
- **Security** via bandit and pip-audit.  

## 2.3 Standards
- PEP8 coding style.  
- QA docs in Markdown, exported to PDF.  
- Accessibility aligned with WCAG (minimal compliance).  

## 2.4 Test Stages
1. Unit Testing  
2. Integration Testing (Python ↔ GeneWeb)  
3. Golden Master Regression  
4. E2E / Performance Testing  
5. Security & Accessibility Testing  

## 2.5 Test Team Organisation
- QA Lead (strategy & reports)  
- Devs (TDD, writing tests)  
- Ops (CI/CD & environments)  

## 2.6 Reviews and Inspections
- Peer review of code & tests (GitHub PRs).  
- Golden Master updates require explicit approval.  

## 2.7 Test Documentation
- QA Strategy (this document).  
- Test Plans & Reports (CI artifacts).  
- Golden files (`tests/golden/*.json`).  

## 2.8 Test Plans
- Day-by-day QA deliverables (0–5).  
- Regression and security emphasis.  

## 2.9 Test Specifications
- Defined test cases per endpoint.  
- Golden outputs captured and versioned.  

## 2.10 Test Scripts
- `pytest` test suites.  
- Bandit / pip-audit config.  

## 2.11 Test Execution
- Automated in GitHub Actions.  
- Manual exploratory testing before defense.  

## 2.12 Suspension and Resumption Criteria
- Suspend tests if GeneWeb backend unavailable.  
- Resume once service restored and stable.  

## 2.13 Entry & Exit Criteria
- Entry: CI pipeline green, environment ready.  
- Exit: All tests pass, coverage >70%, security scans clear.  

## 2.14 Test Results Capture
- Coverage XML, pytest reports, golden diffs.  
- Stored as CI artifacts.  

## 2.15 Test Harnesses
- Docker-compose to spin up GeneWeb + Python.  
- Mock fallback for GeneWeb when unavailable.  

## 2.16 Approach to Regression Testing
- Golden Master as baseline.  
- Automated regression suite in CI.  

## 2.17 Approach to Security Testing
- Bandit for static analysis.  
- Pip-audit for dependencies.  
- Security headers in FastAPI.  

# 3. Test Management

## 3.1 Quality Management
- QA integrated across lifecycle.  
- Peer reviews + CI enforcement.  

## 3.2 Approach to Incident Management
- Issues tracked in GitHub (bugs labeled).  
- Failures in CI → immediate triage.  

## 3.3 Test Metrics
- Coverage percentage.  
- Number of passed/failed tests.  
- Security issues detected.  

## 3.4 Progress Reporting
- Daily QA updates in standups.  
- Weekly QA report shared with stakeholders.  

## 3.5 Test Phase Report
- Generated after each day (0–5).  
- Contains test results, golden diff status.  

## 3.6 Improvement Initiatives
- Expand Golden suite.  
- Automate more E2E workflows.  

---

# 4. Testing Control
- QA Lead validates golden updates.  
- PM validates entry/exit criteria compliance.  

---

# 5. Test Data
- Anonymized data for GDPR compliance.  
- Golden outputs stored in repo under `tests/golden/`.  

---

# 6. Testing Environments
- Dockerized GeneWeb + FastAPI.  
- Local dev + CI GitHub Actions runners.  

---

# 7. Testing Tools

## 7.1 Test Management Tools
- GitHub Projects & Issues.  

## 7.2 Test Automation Tools
- pytest + coverage.  
- pip-audit
- pep8 for linting.  

---
