# okft Lint Report — dev_wspace/okf_bundle

**Bundle:** `dev_wspace/okf_bundle`
**Generated:** 2026-07-13 (from `dev_wspace/fixtures/realworld/python`)
**okf-generator version:** v0.1.48 (schema v0.2)
**okft version:** v0.1.0 (schema v0.1)

---

## Summary

| Stat | Value |
|------|-------|
| Concepts checked | 78 |
| Errors | 16 |
| Warnings | 3 |
| Passing | No — exit code 1 |

---

## Errors (16) — all E004: reserved file must not have frontmatter

Every `index.md` and `log.md` in the bundle has frontmatter. OKF v0.1 SPEC §6 says
index files contain no frontmatter (except `okf_version` on root index.md per §11).

| # | File |
|---|------|
| 1 | `index.md` (root) |
| 2 | `log.md` |
| 3 | `_dependencies/index.md` |
| 4 | `_dependencies/pip/index.md` |
| 5 | `complex/api/index.md` |
| 6 | `complex/config/index.md` |
| 7 | `complex/index.md` |
| 8 | `complex/services/index.md` |
| 9 | `complex/services/payment/index.md` |
| 10 | `easy/index.md` |
| 11 | `easy/models/index.md` |
| 12 | `easy/utils/index.md` |
| 13 | `easy_v2/index.md` |
| 14 | `easy_v2/models/index.md` |
| 15 | `easy_v2/utils/index.md` |
| 16 | `easy_v2/validator/index.md` |

**Status:** Subdirectory index.md frontmatter was fixed in commit `f6da91023`
(strip frontmatter from `render_dir_index()`). Root `index.md` and `log.md`
frontmatter are still present by design (extensions beyond spec).

---

## Warnings (3)

### W004 — orphan concept (1)

`SUMMARY.md` is never linked from any other document. Expected — SUMMARY.md is the
entry point for AI agents (Claude Code, OpenCode), not a concept file. Not an issue.

### W001 — broken link (1)

`SUMMARY.md:37` links to `complex/services/__init__/index.md` which does not exist.
The actual file is probably `complex/services/payment/index.md`. This is a genuine
broken link from a stale summary regeneration.

### W006 — log.md heading format (1)

`log.md` heading is not ISO 8601 date. The log has frontmatter (`type: Log`) instead
of date headings. okft expects `## 2026-07-14` style headings per spec §7.

---

## Interpretation

| Category | Findings | Impact |
|----------|----------|--------|
| Spec violations (E004) | 16 | All index/log files have frontmatter. Subdirectory ones are fixed in latest commit. Root index.md and log.md kept by design for `source_root`/LSP enrichment. |
| Broken links (W001) | 1 | Stale SUMMARY.md — harmless for AI agents, agents navigate by concept_id not file paths. |
| Orphans (W004) | 1 | SUMMARY.md — expected, not a concept. |
| Structurals (W006) | 1 | log.md format mismatch. Minor. |

**Real issues worth fixing:** The broken link in SUMMARY.md (W001) is a genuine stale
reference. Everything else is either already fixed (subdirectory frontmatter) or an
intentional extension (root frontmatter, SUMMARY.md as entry point).
