# OKF Generator — Project Knowledge Base

A comprehensive reference for AI agents working with the okf-generator codebase.
Reading this file gives you full context about architecture, CLI, enrichment pipeline,
parsers, linker, tests, and release process.

**Version:** 0.1.51 | **License:** MIT | **Schema:** OKF v0.2

---

## What is it?

Generates OKF v0.2 knowledge bundles from codebases. Scans source code (18 languages
via AST/tree-sitter) and manifest files (20 formats) into structured markdown that AI
coding agents can read instead of raw source files. Core extraction is fully
deterministic and offline. Optional enrichment passes (LSP and/or LLM) improve
call-graph accuracy and add human-readable summaries.

**The core value:** An average concept lookup drops from ~45,000 tokens (raw file)
to ~1,200 tokens (OKF concept card) — a ~97% reduction.

---

## CLI Commands (24 total)

| Command | Description |
|---------|-------------|
| `okf generate <src> [out]` | Generate OKF bundle (default out: `./okf_bundle`) |
| `okf generate --enrich <mode>` | Generate with LLM enrichment |
| `okf generate --domains <d>` | Generate with domain classification |
| `okf enrich --lsp` | LSP enrichment (caller/callee resolution) |
| `okf enrich --llm [--mode base\|deep\|security]` | LLM enrichment |
| `okf enrich --full` | Shortcut: LSP + LLM deep |
| `okf lsp status\|resolve\|map` | Inspect/test LSP servers |
| `okf lookup <name> [--bundle] [--type] [--tag] [--json]` | Concept search with cache |
| `okf diff <old> <new> [--compact] [--impact]` | Bundle comparison |
| `okf pairs <bundle> [out]` | Convert bundle to training pairs (JSONL) |
| `okf summarize <bundle>` | Regenerate SUMMARY.md only |
| `okf init` | Interactive bundle setup wizard |
| `okf install [agent]` | Install for Claude, Cursor, Copilot, etc. |
| `okf visualize <bundle> [out.html]` | Interactive HTML graph explorer |
| `okf serve [dir] [--port]` | Serve bundle + auto-open viz |
| `okf dashboard <bundle>` | Live bundle browser (FastAPI) |
| `okf mcp <bundle> [--port] [--install]` | MCP server for AI agents |
| `okf ask <question>` | AI-powered Q&A about codebase |
| `okf agent` | Interactive REPL |
| `okf domains [list\|validate]` | List/validate domain rules |
| `okf config [key=val]` | View/set configuration |
| `okf migrate v0.1-to-v0.2` | Schema migration |
| `okf plugin [list\|install\|uninstall]` | Parser plugin management |
| `okf --version` | Print version |

---

## Enrichment Pipeline

The enrichment system lives in `okf/enrich/` and uses a pluggable
**Enricher contract**:

```python
class Enricher(ABC):
    def start(self, bundle_dir, concepts) -> bool    # prepare; False = skip
    def run(self, bundle_dir, concepts) -> EnrichResult  # execute, continue on failure
    def stop(self) -> None                             # cleanup, always safe
```

`EnrichResult(enriched_count, skipped_count, total_count, warnings)` with `.is_partial`.

Orchestrated by `run_enrich()` in `okf/enrich/__init__.py`, which wraps each enricher
in try/finally (never global signal handlers).

### LSP Enrichment — `okf/enrich/lsp.py` (435 lines)

Hand-rolled JSON-RPC client over stdio (no pygls dependency). Spawns one subprocess
per language.

| Step | Detail |
|------|--------|
| Server detection | `shutil.which()` for each entry in `_lsp_map.py` |
| Startup | `initialize` request, 3s timeout → skip server |
| File open | `textDocument/didOpen` with correct `languageId` |
| Query | `textDocument/references` + `textDocument/definition` |
| Mapping | LSP file+line results → concept_id via `source_lines` range containment |
| Writeback | Update `concept.called_by`, re-render with `render_concept()` |

4 servers mapped:

| Lang | Server | Check cmd |
|------|--------|-----------|
| Python | `pyright-langserver --stdio` | `pyright-langserver` |
| Go | `gopls` | `gopls` |
| Rust | `rust-analyzer` | `rust-analyzer` |
| TypeScript/JS | `typescript-language-server --stdio` | `typescript-language-server` |

**Key design decisions:**
- Auto-creates `pyrightconfig.json` at workspace root if missing (pyright needs it)
- Detects project root by walking up for `.git`/`pyproject.toml`
- Per-language `initializationOptions` (pyright gets `include` paths)
- No SIGINT handler in class — cleanup driven by `try/finally` in orchestrator
- `_lang_for()` result cached in `start()` to avoid per-concept `shutil.which()`
- Partial failure: writes per-concept results immediately, reports warnings

### LLM Enrichment — `okf/enrich/llm.py` (368 lines)

OpenAI-compatible client wrapper. Three sub-modes:

| Mode | What it enriches | Source code sent? |
|------|-----------------|-------------------|
| `base` | description, docstring, tags, design_pattern | ❌ (signature only) |
| `deep` | usage_example, side_effects, security, complexity | ✅ (up to 120 lines) |
| `security` | security, complexity (audit only) | ✅ |

- Parallel via `ThreadPoolExecutor` (configurable `max_workers`, default 2)
- Resumable: skips already-enriched fields on re-run
- Token tracking via `_ENRICH_TOKENS` dict
- Body truncated at `_MAX_BODY_LINES = 120`

### Prompt Templates — `okf/enrich/_llm_prompts.py` (141 lines)

All 4 prompts: `ENRICH_PROMPT`, `DEEP_ENRICH_PROMPT`, `SECURITY_PROMPT`, `RELATED_PROMPT`.
Shared `_SECURITY_FIELD_SPEC` ensures prompts can't drift apart.
All enforce strict JSON-only output with no markdown fences.

---

## Language Parsers (17)

Each in `okf/parsers/<lang>.py`. Extend `TreeSitterParser` base class.

| Lang | Parser | Method |
|------|--------|--------|
| Python | `PythonParser` | stdlib `ast` |
| JavaScript/TypeScript | `JSTSParser` | tree-sitter |
| Go | `GoParser` | tree-sitter |
| Java | `JavaParser` | tree-sitter |
| Rust | `RustParser` | tree-sitter |
| Ruby | `RubyParser` | tree-sitter |
| C | `CParser` | tree-sitter |
| C++ | `CppParser` | tree-sitter |
| C# | `CSharpParser` | tree-sitter |
| SQL | `SQLParser` | regex (dialect-tolerant) |
| Swift | `SwiftParser` | tree-sitter |
| Kotlin | `KotlinParser` | tree-sitter |
| PHP | `PHPParser` | tree-sitter |
| Dart | `DartParser` | tree-sitter |
| Scala | `ScalaParser` | tree-sitter |
| Julia | `JuliaParser` | tree-sitter |
| YAML | — | PyYAML |

### Concept Dataclass — `okf/parsers/base.py`

```python
@dataclass
class Concept:
    type: str           # Module | Function | Class | Method | Dependency
    title: str
    description: str
    resource: str        # relative source path
    tags: list[str]
    timestamp: str
    signature: str
    docstring: str
    params: list[dict]   # [{name, annotation, default}]
    returns: str
    source_lines: tuple  # (start_line, end_line)
    concept_id: str      # unique identifier
    methods: list[str]
    calls: list[str]     # callee concept_ids
    called_by: list[str] # caller concept_ids
    related: list[str]   # related concept_ids
    body_extra: dict     # LSP metadata, dependency info, etc.
    # LLM-enriched fields:
    security: str
    complexity: str
    design_pattern: str
    usage_example: str
    side_effects: str
    deprecation_notes: str
    related_semantic: list[str]
```

---

## Cross-Reference Linker — `okf/linker.py` (630 lines)

Runs after scan, before write. Two passes:

### 1. Dependency-to-code linking (`link_dependencies`)
- Builds `{(ecosystem, dep_name): concept_id}` index
- For each Module, normalizes imports per language
- Maps through `LANG_TO_ECOSYSTEMS`: python→pip, javascript→npm, go→go, rust→cargo, java→[maven,gradle], ruby→rubygems
- Filters ~80 well-known stdlib prefixes

### 2. Call-graph edges (`link_calls`)
- Index: `{bare_name: [concept, ...]}`
- Resolution order: same-file → same-domain → globally-unique → ambiguous
- Ambiguous calls stored in `possible_calls` attribute

**Import/call collectors:** Per-language helpers at bottom of linker.py (Python AST, JS/TS tree-sitter, Go, Java, Rust, Ruby).

---

## Manifest Scanner — `okf/manifest_scanner.py`

12 ecosystems: pip, npm, cargo, go, maven, gradle, rubygems, composer, swiftpm, clojars, hex.

Scans for `requirements.txt`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`,
`pom.xml`, `Gemfile`, `build.gradle`, `Package.swift`, `deps.edn`, `mix.exs`,
`project.clj`, `rebar.config`, `CMakeLists.txt`, `Dockerfile`, `docker-compose.yml`.

---

## MCP Server — `okf/mcp_server.py`

Exposes 11 tools: `lookup`, `get_concept`, `find_callers`, `find_callees`,
`list_by_file`, `list_dependencies`, `bundle_info`, `list_by_type`,
`search_by_tag`, `get_related`, `get_manifest_source`.

Runs over stdio (default) or HTTP. Has `--install` flag that registers in
`opencode.json` and `claude_desktop_config.json`.

---

## Domain Classification — `okf/domains/engine.py`

YAML-based rule engine. Rules are pure YAML data — no Python code required for
new domains. Built-in Crossplane rules (8 rules: XRD, Composition V1/V2,
ProviderConfig, Provider, Configuration, ManagedResource).
Match primitives: `has_key`, `match_contains`, `match_pattern`.

---

## Configuration — `okf/config.py`

Files (merged): `~/.config/okf/config.json` ← `.okfconfig` (project-level).

Sections: `llm`, `providers`, `enrich`, `serve`, `lookup`, `mcp`, `pairs`.

Provider resolution cascade: `enrich.{mode}.{key}` → `providers.{name}.{key}` → `llm.{key}`.

Built-in providers: local, openai, anthropic, deepseek, gemini, ollama, lmstudio,
openrouter, dashscope, minimax.

---

## Tests — 415 total

| File | Tests |
|------|-------|
| `tests/test_generator.py` | 123 |
| `tests/test_domain_engine.py` | 38 |
| `tests/test_manifest_scanner.py` | 31 |
| `tests/test_realworld_fixtures.py` | 63 |
| `tests/test_lookup.py` | 21 |
| `tests/test_diff.py` | 11 |
| `tests/test_mcp.py` | 11 |
| `tests/test_init.py` | 4 |
| `tests/test_ignore.py` | 30 |
| `tests/test_frontmatter.py` | 16 |
| `tests/test_update.py` | 12 |

Run: `pytest tests/ -q` (415 passed). Integration: `bash tests/test.sh` (17 phases).

Fixtures: `tests/fixtures/realworld/` (multi-language), `tests/fixtures/complex/`.

---

## Project Files Reference

| File | Purpose |
|------|---------|
| `AGENTS.md` | Instructions for AI agents using this project |
| `CLAUDE.md` | Concise project context for Claude Code |
| `TEST.md` | Full 10-phase integration test specification |
| `RELEASE.md` | Step-by-step release checklist |
| `FUTURE.md` | Roadmap (SAST enrichment, MkDocs replacement, IDE plugins) |
| `CHANGELOG.md` | Version history with feature descriptions |
| `CONTRIBUTING.md` | Contributor guide |
| `SKILL.md` | OpenCode/Claude skill definition |
| `SECURITY.md` | Security policy |

---

## Release Workflow

1. Run `bash tests/test.sh` — must pass 17 phases
2. Run `pytest tests/ -q` — 415 pass
3. Run `ruff check okf/` — clean
4. Bump version in `okf/__init__.py` + `pyproject.toml`
5. Update `CHANGELOG.md` — promote `[Unreleased]` → dated version
6. Rebuild docs: `mkdocs build && cp -r build/docs-site docs/`
7. Generate viz: `okf generate tests/fixtures/realworld _build/bundle && okf visualize _build/bundle _build/viz.html && cp _build/viz.html docs/`
8. Commit, tag (`vX.Y.Z`), push, push --tags
9. CI builds, publishes to PyPI, runs smoke test, creates GitHub Release
10. Run `bash tests/verify-release.sh vX.Y.Z` to check all endpoints

---

## Roadmap (from FUTURE.md)

1. **SAST enrichment** (`okf enrich --sast`) — wrap semgrep/bandit/gosec in Enricher contract
2. **MkDocs replacement** — fix site_url nesting or migrate to mdBook/Starlight
3. **IDE plugins** — VS Code + JetBrains extensions reading `.okf_bundle/`
