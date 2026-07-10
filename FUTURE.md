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

## 4. Tree-sitter WASM in Viz

**Effort:** High (1–2 weeks)

Compile tree-sitter parsers to WebAssembly, bundle them into the viz HTML. The viz graph becomes a **full offline code explorer** — click any concept to see parsed source with syntax highlighting, collapsible scopes, hover-to-reveal signatures. No server needed; the `.okf_bundle/` folder is fully self-contained.

**What it unlocks:** Viz is no longer a static snapshot. It's an interactive IDE-like browser that works from any static host (GitHub Pages, S3, Render). Also enables a VS Code webview extension trivially (same WASM parsers).

---

## 5. IDE Plugins

**Effort:** Very High (2–4 weeks each)

**VS Code extension:** Reads `.okf_bundle/` from workspace root. Shows hover tooltips with docstrings/signatures, call-graph peek, jump-to-def across languages. Uses bundle's cross-reference data (no language server needed).

**JetBrains plugin:** Same concept via IntelliJ plugin SDK.

**What it unlocks:** OKF becomes invisible — developers get codebase-wide context without leaving their editor. Makes the bundle useful for humans, not just AI agents.
