# Performance Analysis: `okf generate` — 157s to 12s

> **Hardware:** Apple Silicon M-series, 8 cores, NVMe SSD  
> **Dataset:** 23 GB workspace, 18,000 source files, 50+ projects  
> **Codebase:** `okf-generator` v0.1.50 · July 2026

**Terms used in this document:** *paths* = every filesystem entry visited (files + dirs); *files* = source files actually parsed; *concepts* = extracted functions, classes, modules, dependencies.

---

## The arc

Running `okf generate` on a real workspace took **157 seconds** the first time. That is too slow to run on every Git push, too slow for interactive use.

By profiling each stage, fixing the current bottleneck, and re-profiling, we cut this to **12 seconds** — a **13× improvement**. The bottleneck migrated four times. Each optimization exposed the next one.

**Important caveats before the headline:**
- The optimized run also does **less useless work** — the baseline indexed 124K concepts including transitive npm dependencies from `node_modules/`. The optimized run correctly excludes vendored code and indexes 41K first-party concepts. This is not purely a speed comparison; it is also a correctness improvement.
- Per-stage multipliers (84×, 5×, 17×, etc.) apply to their own time slices and do not compound to 13×. Stages run sequentially, so fixing one does not shrink the others proportionally.
- Results are on NVMe. Spinning disk or network filesystems will see smaller write-stage gains.

---

## Method

Instrument every stage with `time.perf_counter()`. Run 3 times back-to-back (warm cache), report median. Change one thing. Re-run. Follow the bottleneck.

---

## Stage 1: Filesystem walk — 58s → 0.58s (84×)

The original code used `Path.rglob("*")`:

```python
all_paths = sorted(root.rglob("*"))
```

`rglob("*")` descends into everything — `node_modules`, `.venv`, `.git` — before you get a chance to filter. Of 819,000 paths in our workspace, **781,000 (95%)** were in directories we immediately skipped. The OS spent 55 seconds reading directory entries that were never useful.

We replaced it with `os.walk()` and in-place directory pruning:

```python
for dirpath, dirnames, filenames in os.walk(str(root), topdown=True):
    # Delete from dirnames BEFORE os.walk descends into them
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS
                   and not d.startswith(".")]
    for f in filenames:
        yield Path(dirpath) / f
```

`os.walk` with pruning says "only give me what I need." The difference is not API surface — it is that we never descend into excluded directories at all.

| Metric | Before | After |
|--------|--------|-------|
| Paths visited | 819,000 | 24,435 |
| Wasted traversal | 781,000 (95%) | 0 |
| Time | 58.0s | 0.58s |

We verified that 221 user-written manifest files are still indexed. Only vendored transitive deps (inside `node_modules/`, `.venv/`, `.git/`) are excluded — a correctness improvement, not a regression.

---

## Stage 2: File parsing — 16.7s → 3.4s (5×)

With the walk done in half a second, parsing emerged as the next bottleneck. The tool supports 16 languages via Python `ast` or tree-sitter grammars. The original code parsed each file sequentially:

```python
for path in all_paths:
    file_concepts = parser.parse_file(path, root)
    concepts.extend(file_concepts)
```

Each file is independent, yet we left 7 CPU cores idle. We moved parsing into a `ProcessPoolExecutor`:

```python
with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
    results = pool.map(_mp_parse_file, work_items, chunksize=32)
```

But multiprocessing exposed a pre-existing thread-safety bug. The tree-sitter parsers cached a language object at the class level with a racy `if x is None: x = ...` pattern. Under concurrent access, two threads could initialize simultaneously. We added double-checked locking:

```python
def _lang(self):
    if self.__class__._lang_obj is None:
        with self.__class__._lang_lock:
            if self.__class__._lang_obj is None:
                self.__class__._lang_obj = Language(...)
    return self.__class__._lang_obj
```

The JavaScript/TypeScript parser was worse — it reset `_lang_obj = None` on every `parse_file()` call, creating a data race any time `.js` and `.ts` files were parsed concurrently. We fixed it by never caching the TypeScript grammar (created fresh under the lock) and caching only the JavaScript fallback.

| Metric | Before | After |
|--------|--------|-------|
| Strategy | Sequential | Parallel (8 workers) |
| Files parsed | 4,425 | 4,425 |
| Time | 16.7s | 3.4s |

---

## Stage 3: Cross-reference linking — 9.5s → 0.55s (17×)

The linker builds call graphs and dependency maps. Dependency linking was fast (0.07s). Call-graph resolution was eating **9.5 seconds** — 99.5% of linker time.

Two problems. First:

```python
def _resolve_callee(caller, raw, name_index):
    candidates = name_index.get(bare)       # up to 1,653 candidates
    same_file = [c for c in candidates      # O(n) scan on EVERY call
                 if _same_file(caller, c)]
    ...
```

With 198,000 call sites and some names having 1,653 candidates (`__init__`), these list comprehensions ran millions of times. We precomputed lookup tables for O(1) same-file and same-domain resolution, and added a dict cache keyed by `(resource, domain, raw)`. Cache hit rate: **65%** — 128,000 of 198,000 calls resolved from cache without any scanning.

Second, subtler:

```python
if resolved.concept_id not in caller.calls:   # O(n) on a GROWING list
    caller.calls.append(resolved.concept_id)
```

`caller.calls` is a list. Every `not in` check scans the entire list. As a function accumulates 200+ calls, every subsequent check gets slower. We added a parallel `set` for O(1) membership tests.

| Metric | Before | After |
|--------|--------|-------|
| Resolution | O(n) scans + O(n) dedup | O(1) indexes + cache + set |
| Call sites | 198,000 | 198,000 |
| Cache hit rate | 0% | 65% |
| Time | 9.53s | 0.55s |

---

## Stage 4: Bundle writing — threading (98s → 14s)

The writer produces one `.md` file per concept: 41,000+ concept files + 10,000 directory indexes. The original code wrote them all sequentially, one `write()` syscall at a time.

We moved the loop into a `ThreadPoolExecutor` with 16 workers. File I/O releases the GIL, so writes overlap with near-linear speedup. We also cached already-created parent directories to eliminate ~20,000 redundant `stat()` calls per run:

```python
_created_dirs: set[str] = set()
if parent not in _created_dirs:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _created_dirs.add(parent)
```

| Metric | Before | After |
|--------|--------|-------|
| Strategy | Sequential | Threaded (16 workers) |
| Time | ~98s (baseline) | 14s |

**But we were not done here.** We profiled *inside* the write stage and found a surprise.

---

## Stage 5: PyYAML frontmatter — 9.87s → 0.91s (10.8×)

We instrumented the per-file write function to separate "render" (CPU) from "I/O" (disk):

```
Write stage internal split (after threading but before YAML fix):
  PyYAML frontmatter:    9.87s  (70% of write time)
  Markdown body:         0.49s  (4%)
  I/O (disk writes):     3.7s   (26%)
```

**PyYAML consumed 95% of the render time.** For a flat dict with 6-10 string/list keys, `yaml.safe_dump` does full node-graph analysis, anchor tracking, type detection — complete overkill. We wrote a 140-line schema-specific serializer that produces the same output in one-tenth the time:

```python
def dump_frontmatter(metadata: dict) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {quote_if_needed(str(item))}")
        else:
            lines.append(f"{key}: {quote_if_needed(str(value))}")
    lines.append("---")
    return "\n".join(lines) + "\n"
```

The `quote_if_needed` function handles colons, quotes, YAML 1.1 keywords (`true`, `false`, `null`), leading special chars, multiline, trailing spaces, and date-looking strings. If the dict ever contains an unexpected type, it falls back to `yaml.safe_dump` for that document.

**71 adversarial round-trip tests** validate every fixture through `yaml.safe_load(dump_frontmatter(dict)) == dict`. This runs in CI on every change.

| Metric | Before | After |
|--------|--------|-------|
| Serializer | `yaml.safe_dump` | `dump_frontmatter` |
| Time | 9.87s | 0.91s |
| Tests | — | 71 |

The 14s write stage dropped to **4.1s** — dominated by disk I/O, which was already overlapping across threads.

---

## The progression

```
Stage        Baseline   After walk   After parse  After link  After write  After yaml
                         + parse      + link fix   threading
───────────  ────────   ──────────   ───────────  ──────────  ───────────  ──────────
Walk         58.0s      0.58s        0.58s        0.58s       0.58s        0.58s
Parse        ~17s       3.4s         3.4s         3.4s        3.4s         3.4s
Link         ~1s¹       9.5s²        0.55s        0.55s       0.55s        0.55s
Write        ~81s³      ~81s         ~81s         14s         14s          4.1s
───────────  ────────   ──────────   ───────────  ──────────  ───────────  ──────────
Sum          ~157s      95s          85s          19s         19s          8.6s
Measured     157s       —            —            —           21s          12s
```

Each column represents one optimization on top of the previous. The bottleneck moved: filesystem → parser → linker → YAML serializer.

¹ The baseline linker was fast (~1s) because 86K of 124K concepts were flat dependency entries with no call edges, processed in a single pass.

² After walk pruning excluded vendored deps, only 41K concepts remained — but they had richer cross-references. Link time jumped to 9.5s (Stage 3's starting point). This is not a regression; it is the correct cost of linking real code after removing noise.

³ Baseline stage times marked ~ are reconstructed from later profiling. Only the 157s TOTAL and 58.0s Walk were directly measured in the baseline run. Per-stage approximations do not sum exactly to 157s; the "Sum" row reflects the arithmetic of the estimates shown.

---

## What each optimization contributed

| Change | Before | After | Gain | LOC |
|--------|--------|-------|------|-----|
| `os.walk` + dir pruning | 58.0s | 0.58s | **84×** | 80 |
| `ProcessPoolExecutor` parse | 16.7s | 3.4s | **5×** | 60 |
| Precomputed indexes + resolve cache + set dedup | 9.5s | 0.55s | **17×** | 90 |
| `ThreadPoolExecutor` write + dir cache | ~81s | 14s | **5.8×** | 40 |
| Hand-rolled frontmatter serializer | 9.87s | 0.91s | **10.8×** | 140 + 71 tests |

---

## What we did NOT do

| Suggestion | Why skipped |
|-----------|-------------|
| Rust/PyO3 extension | 12s batch job does not justify build complexity or contributor barrier |
| SQLite/JSONL bundle format | Markdown output is a feature — human-readable, git-friendly, spec-conformant |
| Producer/consumer pipeline | Architectural complexity for ~3s potential gain; write no longer dominates |
| Remove `yaml` dependency entirely | Kept as fallback + oracle for round-trip tests |

---

## Safety nets

Every change was backed by verification:

- **Walk pruning**: Confirmed 221 user-written manifests are still indexed. Only vendored deps excluded.
- **Thread safety**: Double-checked locking on `_lang()`; removed racey `_lang_obj = None` reset in `JSTSParser`.
- **YAML serializer**: 71 round-trip tests with adversarial fixtures; falls back to `yaml.safe_dump` for unexpected types.
- **All changes**: 414 passing tests.

---

## The Numbers

| Metric | Before | After |
|--------|--------|-------|
| **Total time** | **157s** | **12s** |
| **Speedup** | **1×** | **13×** |
| **Concepts indexed** | ~124,000 (incl. vendored) | 41,174 (first-party only) |
| **Source files parsed** | ~4,400 | 4,427 |
| **Bundle size** | 537 MB | 204 MB |
| **Bundle files** | 133,000 | 50,856 |
| **Files changed** | — | 8 files + 2 new |
| **LOC changed** | — | ~660 |
| **Tests added** | — | 71 |
| **Total tests** | 343 | 414 |

---

## Running it

```bash
pip install okf-generator
okf generate ./your-project ./okf_bundle
# Output includes [perf] lines with stage-level timing
```

The interesting part was not any single optimization. Every improvement came from profiling the current bottleneck, fixing it, and profiling again. Each optimization exposed the next one, and the 13× improvement was the cumulative result of those small, measured changes.
