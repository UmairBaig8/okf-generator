# OKF Generator — Test Specification

**Author:** AI agent / CI
**Canonical runner:** `bash tests/test.sh` (generates `TEST_REPORT.html`)
**Fixture corpus:** `tests/fixtures/realworld/` (96 files, 13 languages, 22 projects)
**Unit tests:** `pytest tests/` (173+ tests)

---

## Quick Start

```bash
# Full test suite + HTML report
bash tests/test.sh
open TEST_REPORT.html

# Unit tests only
pip install -e ".[dev]"
pytest tests/ -q
```

---

## Phase 1 — Unit Tests

### 1.1 Lint
```bash
ruff check okf/ --select E,F,W --ignore E501
```
**Verify:** Exit code 0.

### 1.2 Pytest
```bash
python -m pytest tests/ -v 2>&1
```
**Verify:** All tests pass. Record count + time.

### 1.3 Realworld fixture integrity
```bash
python3 -c "
from okf.generator import scan_codebase
from pathlib import Path
c = scan_codebase(Path('tests/fixtures/realworld'))
print(f'{len(c)} concepts')
feats = ['type_params','inheritance','decorators','visibility','fields']
for f in feats:
    print(f'  {f}: {sum(1 for x in c if getattr(x,f))}')
"
```
**Verify:** All features have >0 concepts (generics, inheritance, decorators, visibility, fields).

---

## Phase 2 — CLI: `okf generate`

### 2.1 Realworld (11 langs, 78 files)
```bash
rm -rf /tmp/okf_bundle
okf generate tests/fixtures/realworld /tmp/okf_bundle 2>&1
```
**Verify:**
- Exit code 0. Output shows `Class`, `Function`, `Module`, `Dependency` rows.
- Bundle exists at `/tmp/okf_bundle` with `SUMMARY.md`, `index.md`, `log.md`.

### 2.2 Python easy project
```bash
okf generate tests/fixtures/realworld/python/easy /tmp/py_bundle 2>&1
```
**Verify:** Functions (`slugify`, `chunk_list`), Class (`User`), Dependency from `requirements.txt`.

### 2.3 Enrich flag does not crash
```bash
okf generate tests/fixtures/realworld/python/easy /tmp/enrich_bundle --enrich 2>&1
```
**Verify:** Exit 0. Warning about missing API key, but no traceback. Bundle written with all concepts.

### 2.4 Empty directory
```bash
mkdir -p /tmp/empty_test
okf generate /tmp/empty_test /tmp/empty_bundle 2>&1
```
**Verify:** Exit 0. Warning about no recognized files. Bundle written.

### 2.5 Non-existent path
```bash
okf generate /tmp/nope_test /tmp/nope_bundle 2>&1
```
**Verify:** Graceful error (exit 1, no traceback).

---

## Phase 3 — CLI: `okf lookup`

Use bundle from Phase 2.1.

### 3.1 Exact name
```bash
okf lookup --bundle /tmp/okf_bundle --compact Paginated 2>&1
```
**Verify:** Returns `[Class] Paginated` (Rust generic).

### 3.2 Type filter
```bash
okf lookup --bundle /tmp/okf_bundle --type Dependency --compact 2>&1 | head -5
```
**Verify:** Only `[Dependency]` rows.

### 3.3 Tag filter
```bash
okf lookup --bundle /tmp/okf_bundle --tag lang:python --compact 2>&1 | head -5
```
**Verify:** Shows Python concepts.

### 3.4 File filter
```bash
okf lookup --bundle /tmp/okf_bundle --file utils.py --compact 2>&1 | head -5
```
**Verify:** Returns concepts from `utils.py`.

### 3.5 JSON output
```bash
okf lookup --bundle /tmp/okf_bundle --json Paginated 2>&1 | python3 -m json.tool
```
**Verify:** Valid JSON with `type`, `title`, `signature`, `tags` fields.

### 3.6 No-match
```bash
okf lookup --bundle /tmp/okf_bundle ZZZZ_NOT_FOUND 2>&1
```
**Verify:** Exit 1. "No concepts found".

### 3.7 Fuzzy / camelCase / acronym search
```bash
# Subword match: "calc" finds "Calculator"
okf lookup --bundle /tmp/okf_bundle --compact calc 2>&1
```
**Verify:** `Calculator` appears in results.

```bash
# CamelCase token match: "repo" finds "UserRepository", "OrderRepo"
okf lookup --bundle /tmp/okf_bundle --compact repo 2>&1
```
**Verify:** At least one `*Repo*` or `*Repository` result.

```bash
# Acronym match: "ur" finds "UserRepository"
okf lookup --bundle /tmp/okf_bundle --compact ur 2>&1
```
**Verify:** `UserRepository` or similar appears.

```bash
# Exact flag rejects fuzzy: must match full title
okf lookup --bundle /tmp/okf_bundle --exact calc 2>&1; echo "exit=$?"
```
**Verify:** No results. Exit code 1.

### 3.8 Cache miss → hit
```bash
time okf lookup --bundle /tmp/okf_bundle --compact Paginated 2>&1
time okf lookup --bundle /tmp/okf_bundle --compact Paginated 2>&1
```
**Verify:** Second run is visibly faster. `.okf_lookup_cache.json` exists.

---

## Phase 4 — CLI: `okf pairs` + `okf summarize`

### 4.1 Static pairs
```bash
SKIP_SYNTH=1 okf pairs /tmp/okf_bundle /tmp/pairs.jsonl 2>&1
```
**Verify:** Exit 0. Output shows `codegen`, `crosslink`, `summarize` counts.
```bash
head -1 /tmp/pairs.jsonl | python3 -c "import json,sys; d=json.loads(sys.stdin.readline()); assert 'messages' in d; print('OK')"
```

### 4.2 Summarize
```bash
okf summarize /tmp/okf_bundle 2>&1
```
**Verify:** Exit 0. `SUMMARY.md` rewritten.

---

## Phase 5 — CLI: `okf visualize`

### 5.1 Generate viz
```bash
okf visualize /tmp/okf_bundle /tmp/viz.html 2>&1
ls -lh /tmp/viz.html
```
**Verify:** HTML file > 100 KB (contains embedded graph data).

---

## Phase 6 — CLI: `okf diff`

### 6.1 Real version diff (v1 → v2)
```bash
okf generate tests/fixtures/realworld/python/easy /tmp/v1 2>/dev/null
okf generate tests/fixtures/realworld/python/easy_v2 /tmp/v2 2>/dev/null
okf diff /tmp/v1 /tmp/v2 --compact 2>&1
```
**Verify:** Shows Added (4): `batched`, `validate_email`, `validate_phone`, `validator` module. Changed (1): `utils` module doc.

---

## Phase 7 — CLI: `okf mcp` + `okf serve` + `okf init`

### 7.1 MCP server
```bash
okf mcp /tmp/okf_bundle &
MCP_PID=$!
sleep 1
# Test initialize
echo '{"id":1,"method":"initialize"}' | python3 -c "
import json, sys
# MCP uses stdin/stdout transport
" 2>&1 || echo "MCP started (PID $MCP_PID)"
kill $MCP_PID 2>/dev/null || true
```

### 7.2 Serve
```bash
okf serve /tmp/okf_bundle --port 9876 &
SERVE_PID=$!
sleep 1
curl -s --max-time 2 http://127.0.0.1:9876/ 2>&1 | head -1
kill $SERVE_PID 2>/dev/null || true
```

### 7.3 Init wizard
```bash
echo "" | okf init /tmp/init_test 2>&1
```
**Verify:** No crash. Bundle created or graceful exit.

---

## Phase 8 — Viz source code feature

### 8.1 Source code in viz
```bash
# Check that viz.html contains embedded source code
grep -c '"code":"' /tmp/viz.html || echo "0 code entries (no source files found at viz gen path)"
```
**Verify:** May be 0 if source files aren't at the resolved path. When they are, each entry is the full file content.

### 8.2 Viz generation must never crash
```bash
# Run from repo root to ensure source paths resolve
cd "$(git rev-parse --show-toplevel)"
okf generate tests/fixtures/realworld /tmp/viz_crash_test 2>/dev/null
okf visualize /tmp/viz_crash_test /tmp/viz_crash_test.html 2>&1
```
**Verify:** Exit 0. No `PermissionError`, `KeyError`, or traceback. If it crashes, check `visualize.py` source-code lookup for permission-guarded `Path.exists()` calls or search-bases that scan `/tmp/`.

---

## Phase 9 — CLI: `okf enrich` (standalone, no re-scan)

### 9.1 Security mode
```bash
okf generate tests/fixtures/realworld /tmp/enrich_bundle 2>/dev/null
okf enrich /tmp/enrich_bundle --mode security --src tests/fixtures/realworld 2>&1
```
**Verify:** Exit 0. Logs show "security audit complete".

### 9.2 Security mode with --force re-audit
```bash
okf enrich /tmp/enrich_bundle --mode security --force 2>&1
```
**Verify:** Re-audits already-audited concepts. Logs show patched > 0.

### 9.3 Deep enrich mode
```bash
okf enrich /tmp/enrich_bundle --mode deep 2>&1
```
**Verify:** Exit 0. Logs show "enrich complete".

### 9.4 Full enrich mode
```bash
okf enrich /tmp/enrich_bundle --mode full 2>&1
```
**Verify:** Exit 0. Logs show both enrich and (if semantic_related enabled) related-linking.

### 9.5 `--enrich` with mode qualifier
```bash
okf generate tests/fixtures/realworld/python/easy /tmp/mode_bundle --enrich deep 2>&1
```
**Verify:** Exit 0. Bundle written. Logs show "LLM enrichment enabled" + "To enrich".

### 9.6 `--enrich` unknown mode
```bash
okf generate tests/fixtures/realworld /tmp/fail_bundle --enrich bogus 2>&1; echo "exit=$?"
```
**Verify:** Exit code 1. Error message about unknown mode.

---

## Phase 10 — Production Checklist

| Area | Check |
|------|-------|
| `.okf_lookup_cache.json` ignored | `grep -q "okf_lookup_cache" .gitignore` |
| Version consistency | `grep -E "version" okf/__init__.py pyproject.toml` — both same |
| No stale `.pyc` files | `find . -name "*.pyc" -not -path "./.venv/*" -not -path "./dev_wspace/*"` |
| Realworld fixture scan | pytest `test_realworld_fixtures.py` — 43 tests covering all features |
| C# interfaces extracted | Lookup `IOrderRepo` in realworld/csharp/complex bundle |
| Provider config unit tests | `pytest tests/test_generator.py -k "resolve_provider or _get_multi" -q` — 7 tests |
| Provider resolution cascade | Verify `enrich.{mode}.{key} → providers.{name}.{key} → llm.{key}` in `.okfconfig` |
| Built-in provider URLs | `providers.anthropic`, `providers.deepseek`, `providers.openai`, etc. all have valid base_urls |

---

## Reporting

After completing all phases, verify:

```bash
bash tests/test.sh
open TEST_REPORT.html
```

The canonical report lives in `TEST_REPORT.html` (auto-generated by `test.sh`). It covers all 17 phases and is attached to every GitHub Release.
