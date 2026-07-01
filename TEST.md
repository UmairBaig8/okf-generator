# OKF Generator — Production Test Specification

**Author:** AI agent / CI  
**Work dir:** `./dev_wspace` (scratch directory, not versioned)  
**Test codebase:** `./dev_wspace/AgentBox` (TypeScript monorepo, 369 files, includes `package.json`)  
**Self-test codebase:** `./` (okf-generator itself, Python)  
**Report output:** `./dev_wspace/OKF_TEST_REPORT.md` (overwrite each run)

---

## Phase 0 — Setup

### 0.1 Clean slate
```bash
WORK="$(pwd)/dev_wspace"
rm -rf "$WORK/.venv" "$WORK/okf_bundle" "$WORK/OKF_TEST_REPORT.md"
```

### 0.2 Create and activate venv, install okf
```bash
python3 -m venv "$WORK/.venv"
source "$WORK/.venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -e ".[dev,llm]"
```

### 0.3 Verify CLI
```bash
okf --help  # must print usage
```

---

## Phase 1 — Lint + Unit Tests

### 1.1 Ruff lint
```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo "$WORK/..")"
ruff check okf/ --select E,F,W --ignore E501 2>&1
```

**Verify:**
- Exit code 0 (no lint errors).

### 1.2 Pytest
```bash
python -m pytest tests/ -v 2>&1
```

**Verify:**
- All tests pass (exit code 0).
- Record test count and time.

---

## Phase 2 — `okf generate` (Static Extraction)

### 2.1 AgentBox (TS/JS + manifest deps)
```bash
rm -rf "$WORK/okf_bundle"
okf generate "$WORK/AgentBox" "$WORK/okf_bundle" 2>&1
```

**Verify:**
- Exit code 0.
- Output shows: `Class`, `Function`, `Module`, `Dependency` rows.
- `Dependency` count > 0 (npm deps from `package.json`).
- Bundle dir exists at `$WORK/okf_bundle`.

### 2.2 Bundle structure
```bash
ls "$WORK/okf_bundle/"  # must show: SUMMARY.md, index.md, log.md, packages/
```

**Verify:**
- `SUMMARY.md` exists, contains `## Stats` and `## Domain Map` sections.
- `index.md` exists, lists top-level dirs.
- `log.md` exists, contains timestamp and concept count.
- Every subdirectory has its own `index.md`.

### 2.3 Dependency concept file
```bash
cat "$WORK/okf_bundle/npm:express.md" 2>/dev/null || cat "$WORK/okf_bundle/"*":express.md" 2>/dev/null
```

**Verify:**
- Frontmatter has `type: Dependency`, `title: express`, `resource: packages/.../package.json`, `tags` with `ecosystem:npm`, `type:Dependency`, `manifest:package.json`.
- Body contains a table with `Ecosystem`, `Version constraint`, `Source manifest`, `Dev dependency` rows.

### 2.4 Empty directory
```bash
mkdir -p /tmp/okf_test/empty
okf generate /tmp/okf_test/empty /tmp/okf_test/bundle_empty 2>&1
```

**Verify:**
- Exit code 0 (NOT a crash).
- Output says "No recognized source files" warning.
- Bundle is written: `index.md`, `log.md`, `SUMMARY.md` all exist.
- `index.md` contains the bundle name, not an error.

### 2.5 Non-existent path
```bash
okf generate /tmp/okf_test/nope /tmp/okf_test/bundle_nope 2>&1
```

**Verify:**
- Returns empty concepts list (no crash).
- Exit code 0.

### 2.6 Python-only extraction (self-test)
```bash
okf generate "$(pwd)" /tmp/okf_test/bundle_self 2>&1
```

**Verify:**
- Contains `Python` concepts with `lang:python` tags.
- `Class`, `Function`, `Module` counts > 0.
- `Dependency` concepts from `pyproject.toml` > 0.
- `SQL` concepts from test fixtures > 0 (if `migrations/` discovered).

### 2.7 Version stamping
```bash
head -1 "$WORK/okf_bundle/SUMMARY.md" | grep -c "okf_version"
```

**Verify:**
- `okf_version` appears in SUMMARY.md frontmatter.
- Tags include `git:branch:` (AgentBox bundles may show `branch:main`).

### 2.8 SQL parser
```bash
okf lookup --bundle "$WORK/okf_bundle" --type Function --tag lang:sql 2>&1 | head -5
```

**Verify:**
- No SQL in AgentBox (expect no results). This is a negative test confirming no crash.
- Use the self-test bundle instead:
```bash
okf lookup --bundle /tmp/okf_test/bundle_self --type Function --tag lang:sql 2>&1 | head -5
```

---

## Phase 3 — `okf lookup` (Concept Search)

### 3.1 Cache miss (first lookup, writes cache)
```bash
time okf lookup --bundle "$WORK/okf_bundle" --compact SandboxManager 2>&1
```

**Verify:**
- Returns results with `[Class   ] SandboxManager`.
- `.okf_lookup_cache.json` now exists in bundle dir.

### 3.2 Cache hit (subsequent lookup, faster)
```bash
time okf lookup --bundle "$WORK/okf_bundle" --compact SandboxManager 2>&1
```

**Verify:**
- Same results.
- Elapsed time is **visibly faster** than the first run (≤60% of cache-miss time).

### 3.3 Bypass cache (`--no-cache`)
```bash
time okf lookup --bundle "$WORK/okf_bundle" --no-cache --compact SandboxManager 2>&1
```

**Verify:**
- Same results.
- Time is comparable to the original cache-miss time (not as fast as cache hit).

### 3.4 Type filter
```bash
okf lookup --bundle "$WORK/okf_bundle" --type Class --compact SandboxManager 2>&1
```

**Verify:**
- Only `Class` type results.
- If results exist, they contain `[Class   ]`.

### 3.5 Tag filter
```bash
okf lookup --bundle "$WORK/okf_bundle" --tag lang:manifest --compact 2>&1 | head -5
```

**Verify:**
- Shows `[Dependency]` concepts.

### 3.6 File filter
```bash
okf lookup --bundle "$WORK/okf_bundle" --file package.json --compact 2>&1 | head -5
```

**Verify:**
- Returns Dependency concepts with `resource` containing `package.json`.

### 3.7 JSON output
```bash
okf lookup --bundle "$WORK/okf_bundle" --json SandboxManager 2>&1 | python3 -m json.tool | head -20
```

**Verify:**
- Valid JSON.
- Contains: `type`, `title`, `description`, `resource`, `tags`, `signature`, `docstring`, `methods`, `returns` keys.

### 3.8 Full detail view
```bash
okf lookup --bundle "$WORK/okf_bundle" --limit 1 --full axios 2>&1 | head -10
```

**Verify:**
- Output starts with `---` (frontmatter).
- Contains raw markdown of the concept file.

### 3.9 Fuzzy / no-match
```bash
okf lookup --bundle "$WORK/okf_bundle" NoSuchThing12345 2>&1
```

**Verify:**
- Exit code 1.
- `stderr` says "No concepts found".

### 3.10 Non-existent bundle
```bash
okf lookup --bundle ./does_not_exist --compact SandboxManager 2>&1
```

**Verify:**
- Falls through to fallback paths (or errors gracefully).
- Does NOT crash with traceback.

### 3.11 Limit
```bash
okf lookup --bundle "$WORK/okf_bundle" --limit 3 --compact manager 2>&1
```

**Verify:**
- Exactly 3 results (or fewer if < 3 exist).

### 3.12 Type Dependency filter
```bash
okf lookup --bundle "$WORK/okf_bundle" --type Dependency --compact 2>&1 | head -5
```

**Verify:**
- Only `[Dependency]` rows.
- `Dependency` type appears in the output header.

---

## Phase 4 — `okf pairs` (Training Data)

### 4.1 Static pairs
```bash
SKIP_SYNTH=1 okf pairs "$WORK/okf_bundle" "$WORK/pairs_static.jsonl" 2>&1
```

**Verify:**
- Exit code 0.
- Output shows counts for `codegen`, `crosslink`, `summarize` pair types.
- File written and non-empty.
- Each line is valid JSON with `messages` array.

### 4.2 Pair format (spot-check)
```bash
head -1 "$WORK/pairs_static.jsonl" | python3 -c "import json,sys; d=json.loads(sys.stdin.readline()); assert 'messages' in d; print(f'OK: {len(d[\"messages\"])} turns, type={d.get(\"pair_type\",\"?\")}')"
```

**Verify:**
- No exception from assertion.
- Prints at least "OK".

### 4.3 Dependency concepts skipped in codegen/summarize (implicit)
```bash
grep -c '"Dependency"' "$WORK/pairs_static.jsonl" || echo "0 Dependency pairs (expected)"
```
- Dependency concepts shouldn't appear in codegen/summarize pairs.

---

## Phase 5 — `okf summarize` (Summary Regeneration)

### 5.1 Regenerate
```bash
cp "$WORK/okf_bundle/SUMMARY.md" "$WORK/okf_bundle/SUMMARY.md.bak"
okf summarize "$WORK/okf_bundle" 2>&1
```

**Verify:**
- Exit code 0.
- Output says `SUMMARY.md written`.
- File still valid (compare content — stats may differ slightly if concepts changed).

### 5.2 Only SUMMARY.md touched
```bash
[ -f "$WORK/okf_bundle/index.md" ] && echo "index.md intact"
[ -f "$WORK/okf_bundle/log.md" ] && echo "log.md intact"
```

**Verify:**
- `index.md`, `log.md`, all concept `.md` files still exist.
- Only `SUMMARY.md` was modified.

```bash
rm -f "$WORK/okf_bundle/SUMMARY.md.bak"
```

---

## Phase 6 — Edge Cases

### 6.1 `okf generate` on directory with only unsupported files
```bash
mkdir -p /tmp/okf_test/only_txt
echo "hello" > /tmp/okf_test/only_txt/notes.txt
echo "world" > /tmp/okf_test/only_txt/data.csv
okf generate /tmp/okf_test/only_txt /tmp/okf_test/bundle_txt 2>&1
```

**Verify:**
- Exit code 0.
- "No recognized source files" warning.
- Valid bundle written with `index.md`, `log.md`, `SUMMARY.md`.
- `index.md` shows the directory (empty subdirectory handling).

### 6.2 Cache invalidation on bundle change
```bash
# Touch a concept file to change mtime
touch "$WORK/okf_bundle/"*.md
time okf lookup --bundle "$WORK/okf_bundle" --compact SandboxManager 2>&1
```

**Verify:**
- Cache is invalidated (mtime changed), re-parses and rewrites cache.
- Time is closer to cache-miss than cache-hit speed.
- `.okf_lookup_cache.json` still exists after.

### 6.3 Corrupt cache resilience
```bash
echo "garbage" > "$WORK/okf_bundle/.okf_lookup_cache.json"
okf lookup --bundle "$WORK/okf_bundle" --compact SandboxManager 2>&1
```

**Verify:**
- No crash or traceback.
- Results returned correctly.
- Cache file overwritten with valid JSON.

---

## Phase 7 — Cleanup

```bash
rm -rf /tmp/okf_test
```

---

## Production Checklist

| Area | Check |
|------|-------|
| No file is world-writable | `find .venv -perm /o=w -ls | grep -v ".DS_Store"` should be empty or acceptable |
| `.okf_lookup_cache.json` is ignored | `grep -q "okf_lookup_cache" .gitignore` |
| `uv.lock` not committed | If exists, check `.gitignore` or keep untracked |
| Version consistency | `grep -E "version" okf/__init__.py pyproject.toml` — both same |
| No stale `.pyc` files | `find . -name "*.pyc" -not -path "./.venv/*" -not -path "./dev_wspace/*"` should be empty |

---

## Reporting

After completing all phases, produce `./dev_wspace/OKF_TEST_REPORT.md` with:

- **Header:** Date, env (macOS/Linux, Python version, package version), test codebase summary.
- **Phase 1–7 tables:** Each test case as a row with Status (✅ PASS / ❌ FAIL / 🟡 WARN), Detail column with actual output or key observation.
- **Edge cases:** Specific mention of empty-dir, non-existent-dir, only-unsupported-files, corrupt cache, cache invalidation.
- **Timing table:** Compare cache-miss vs cache-hit vs --no-cache times.
- **Summary section:** Overall PASS/FAIL, test count, any blockers found.
