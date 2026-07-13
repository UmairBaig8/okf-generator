# Future Plans

Ordered by development effort (easiest first).

---

## ~~1. CI/CD Realworld Bundle Auto-Publish~~ ✅ Done (v0.1.44)

**What was done:** Extended `.github/workflows/demo-viz.yml` to generate `docs/okf_bundle/` from `tests/fixtures/realworld/` on every push to `main`. Added bundle verification (≥10 concept files). Landing page "Try it live" section now has a "Live Bundle" link. Updated `.gitignore` to un-ignore `docs/okf_bundle/`.

---

## ~~2. User-Facing Auto-Bundle Template~~ ✅ Done (v0.1.44)

**What was done:** Created `docs/examples/okf-auto-bundle.yml` — a ready-to-copy workflow. Updated `docs/user-guide/ci-cd.md` with the full template and explanation. Updated README link to point to new CI/CD doc.

---

## ~~3. v0.2 Schema Bump~~ ✅ Done (v0.1.44)

**What was done:**
- Bumped `"0.1"` → `"0.2"` in all generator emission points (4 locations)
- Added `okf_version`, `concept_id`, `language`, `status` to every concept frontmatter
- Added `status` field to `Concept` dataclass
- Merged `## Related`, `## Calls`, `## Called By` sections into a single `## Relationships` table with typed edges (related, calls, called_by, related (AI))
- Updated `lookup.py` and `pairs.py` to read `relationships` section (with v0.1 fallback)
- Created `okf migrate v0.1-to-v0.2` command with `--dry-run` support
- Updated `bundle-format.md` doc with v0.2 schema

---

## ~~4. `okf agent` REPL~~ ✅ Done (v0.1.44)

**What was done:**
- Created `okf/agent.py` — interactive REPL with rich card output, slash commands (`/lookup`, `/source`, `/calls`, `/called-by`, `/related`, `/save`, `/export`, `/history`, `/clear`, `/resume`, `/sessions`)
- Persistent sessions saved to `~/.okf/sessions/ses_*.json`
- LLM-powered Q&A with context-aware follow-ups (reuses `_search_context` + `_ask_llm` from `okf/ask.py`)
- Session export to JSON or Markdown
- Auto-save every 4 exchanges
- Wired into CLI as `okf agent`

**What it unlocks:** Replaces the "grep files → read sources" loop entirely. Agent (human or AI) stays inside `okf` for the whole exploration flow.

---

## ~~4. Tree-sitter WASM in Viz~~ ✅ Done (v0.1.44)

**What was done:**
- Added `web-tree-sitter` + per-language WASM parsers loaded from jsDelivr CDN (10 languages: python, js, ts, ruby, rust, go, java, cpp, c, php; remaining 7 fall back to source view)
- Code panel now has a "Source" / "Parse Tree" tab switcher
- Parse Tree renders a collapsible named AST tree with syntax-colored tokens
- Deeply nested nodes auto-collapse for readability
- Falls back gracefully if WASM fails to load (network issue, unsupported lang)
- All 242 tests pass

**What it unlocks:** Viz is no longer a static snapshot. It's an interactive AST browser — click any concept, switch to Parse Tree, see the full tree-sitter parse tree with collapsible scopes and syntax highlighting. Works offline after first load (CDN-cached WASM).

---

## 5. SAST Enrichment (`okf enrich --sast`)

**Effort:** Low (1–2 days)

**What:** Wrap deterministic SAST tools (semgrep, bandit, gosec) in the same `Enricher` contract used by LSP and LLM. Each tool becomes a `SastEnricher(Enricher)` with `start/run/stop` lifecycle. Structured CWE/severity output injected into concept frontmatter alongside LSP call graphs and LLM summaries.

**Why:** LSP resolves *what* calls *what*. SAST resolves *which constructs* are *vulnerable*. Combined they produce a bundle with compiler-accurate call graphs + deterministic security findings + LLM behavioural summaries — three orthogonal passes, one pipeline.

**Design:** `okf/enrich/_sast_map.py` (ext → tool config), `okf/enrich/sast.py` (subprocess runner, semgrep JSON → concept mapping, CWE→severity table). `okf enrich --sast` flag.

---

## 6. MkDocs Replacement / Static Site Generator

**Effort:** Medium (3–5 days)

**What:** Replace MkDocs with a faster, simpler static site generator. The current docs-site build has two issues: (a) deep nested `docs-site/docs-site/` path duplication from `site_url` config, (b) build times scale poorly with 1000+ bundle `.md` files.

**Options:**
- **MkDocs config fix** — adjust `site_url`, exclude `okf_bundle/` from nav, add `not_in_nav` plugin. Lowest effort.
- **Move to mdBook** (Rust) — single binary, no Python deps, native search, gitbook-style sidebar. Used by Rust ecosystem.
- **Starlight (Astro)** — component-based, MDX support, better for interactive docs. Heavier build but prettier output.
- **Plain HTML template** — like `docs/index.html` — custom build script generates nav from filesystem. Full control, zero framework churn.

**Priority:** Low — current docs-site is functional. This is a DX improvement for maintainers, not users.

---

## 7. IDE Plugins

**Effort:** Very High (2–4 weeks each)

**VS Code extension:** Reads `.okf_bundle/` from workspace root. Shows hover tooltips with docstrings/signatures, call-graph peek, jump-to-def across languages. Uses bundle's cross-reference data (no language server needed).

**JetBrains plugin:** Same concept via IntelliJ plugin SDK.

**What it unlocks:** OKF becomes invisible — developers get codebase-wide context without leaving their editor. Makes the bundle useful for humans, not just AI agents.
