# OKF Generator — Test Report

**Date:** 2026-07-19T20:52:29Z
**Env:** Darwin / Python 3.14.4
**Version:** v0.1.50-6-g99a64fd4d
**Fixture:** tests/fixtures/realworld (96 files, 13 languages)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 17 |
| Passed | 17 |
| Failed | 0 |
| Skipped | 0 |

---


### Phase 1: Unit Tests

| Test | Status | Detail |
|------|--------|--------|
| pytest — all tests passed | ✅ PASS | |

### Phase 2: CLI Integration

| Test | Status | Detail |
|------|--------|--------|
| okf generate — bundle created | ✅ PASS | |
| okf lookup Paginated — found | ✅ PASS | |
| okf lookup --type Dependency — found | ✅ PASS | |
| okf lookup --json Paginated — valid JSON | ✅ PASS | |
| okf pairs (static) — generated | ✅ PASS | |
| okf summarize — regenerated | ✅ PASS | |
| okf init — ran without crash | ✅ PASS | |
| okf --help — shows usage | ✅ PASS | |
| okf --version — shows version | ✅ PASS | |

### Phase 3: Visualization

| Test | Status | Detail |
|------|--------|--------|
| okf visualize — generated (1483 KB) | ✅ PASS | |

### Phase 4: MCP & Serve

| Test | Status | Detail |
|------|--------|--------|
| okf mcp — responds on port 19876 | ✅ PASS | |
| okf serve — running (no HTTP response) | ✅ PASS | |

### Phase 5: Bundle Diff

| Test | Status | Detail |
|------|--------|--------|
| okf diff — shows changes between v1 and v2 | ✅ PASS | |

### Phase 6: Edge Cases

| Test | Status | Detail |
|------|--------|--------|
| okf generate (empty dir) — no crash | ✅ PASS | |
| okf generate (non-existent) — graceful error (exit 1) | ✅ PASS | |
| okf generate (.txt only) — no crash | ✅ PASS | |
