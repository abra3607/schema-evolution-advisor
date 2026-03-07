# Security Audit -- Cross-Project Findings

Scan date: 2026-03-07
Scope: 7 Python projects at /root

## Findings

### 1. Subprocess flag injection -- roadmap-entropy

**File:** roadmap-entropy/src/roadmap_entropy/history.py
**Severity:** Medium
**Issue:** User-supplied git refs are passed to subprocess calls without a -- separator, allowing flag injection (e.g. a ref named --exec=... could inject arbitrary git flags).
**Fix:** Add -- before positional arguments in all subprocess git calls.

### 2. Overly broad exception handler -- dep-risk-scanner

**File:** dep-risk-scanner/src/dep_risk_scanner/scanner.py
**Severity:** Low
**Issue:** except (httpx.HTTPError, Exception) catches all exceptions, silently swallowing programming errors (TypeError, KeyError, etc.) that should propagate.
**Fix:** Remove Exception from the tuple; catch only httpx.HTTPError (or add specific expected exceptions).

### 3. Missing .env in .gitignore -- all 7 projects

**Severity:** Medium
**Issue:** No project excludes .env or .env.* files in .gitignore. If a developer creates a .env with API keys or database credentials, it could be committed and pushed.
**Fix:** Add .env and .env.* to each project's .gitignore. (Fixed in this repo.)

### 4. Bare except Exception: continue -- test-flakiness-analyzer

**File:** test-flakiness-analyzer/src/test_flakiness_analyzer/parser.py
**Severity:** Low
**Issue:** Broad exception handler silently skips files that fail to parse, hiding real errors (e.g. permission issues, corrupted files).
**Fix:** Narrow to specific exceptions (SyntaxError, OSError, UnicodeDecodeError).

### 5. Bare except Exception -- schema-evolution-advisor (this repo)

**File:** src/schema_evolution_advisor/parser.py:67
**Severity:** Low
**Issue:** is_alembic_migration() caught all exceptions when reading files, masking programming errors.
**Fix:** Narrowed to (OSError, UnicodeDecodeError). (Fixed in this PR.)

## Positive Findings

- defusedxml usage: test-flakiness-analyzer uses defusedxml instead of stdlib xml -- prevents XXE attacks.
- yaml.safe_load: roadmap-entropy uses yaml.safe_load (not yaml.load) -- prevents arbitrary code execution via YAML deserialization.
- No shell=True: All subprocess calls across all 7 projects use list form, avoiding shell injection.

## Recommendations

1. Add -- separators in roadmap-entropy subprocess git calls.
2. Narrow exception handlers in dep-risk-scanner and test-flakiness-analyzer.
3. Add .env / .env.* to .gitignore in all remaining projects.
