# CLI Reference

## Global

```bash
okf --help              Show available commands
okf <command> --help    Show options for a specific command
okf --version           Show version and exit
```

---

## `okf generate`

```bash
okf generate <source_dir> [output_dir] [--exclude <dir> ...]
```

Scans a source directory and produces an OKF v0.2 knowledge bundle.

| Option | Description |
|--------|-------------|
| `--summarize <bundle_dir>` | Regenerate SUMMARY.md only (no re-scan) |
| `--exclude <dir>` | Skip directories matching this name (repeatable) |

**Environment variables (LLM enrichment):**

| Variable | Default | Description |
|----------|---------|-------------|
| `OKF_ENRICH=1` | — | Enable LLM enrichment |
| `OKF_BASE_URL` | `https://api.anthropic.com/v1` | OpenAI-compat endpoint |
| `OKF_API_KEY` | — | API key |
| `OKF_MODEL` | `claude-sonnet-4-6` | Model name |
| `OKF_MAX_WORKERS` | `2` | Parallel workers |

---

## `okf enrich`

```bash
okf enrich [--lsp] [--llm] [--full] [--mode base|deep|security] [--bundle <dir>] [--src <path>]
```

Enrich an existing bundle with LSP and/or LLM passes.  At least one of `--lsp` or `--llm` must be specified.

| Option | Description |
|--------|-------------|
| `--lsp` | Run LSP enrichment (caller/callee resolution via local language servers) |
| `--llm` | Run LLM enrichment (descriptions, summaries, security audit) |
| `--full` | Shortcut for `--lsp --llm --mode deep` |
| `--mode` | LLM mode: `base` (default, no source code), `deep` (with source), `security` (audit only) |
| `--bundle PATH` | Bundle directory (default: `./okf_bundle`) |
| `--src PATH` | Source code root (read from bundle index.md if omitted) |
| `--file PATH` | Filter: only enrich concepts from this source file |
| `--concept ID` | Filter: only enrich this specific concept |

**Examples:**

```bash
# LSP only (free, deterministic)
okf enrich --lsp

# LLM only (safe, no source code sent)
okf enrich --llm

# LSP + LLM deep (maximum accuracy)
okf enrich --full

# With explicit paths
okf enrich --lsp --bundle /tmp/my_bundle --src /home/user/project
```

---

## `okf lsp`

```bash
okf lsp [status|resolve|map]
```

Inspect and test Language Server Protocol servers available on this machine.

| Subcommand | Description |
|------------|-------------|
| `status` | Table of detected LSP servers — shows which are installed |
| `resolve FILE:LINE:COL` | One-shot LSP resolution for a specific file location |
| `map` | Display the extension-to-server command mapping |

**Examples:**

```bash
okf lsp status
okf lsp resolve src/app.py:42:5
okf lsp map
```

---

## `okf update`

```bash
okf update <source_dir> [output_dir]
```

Incremental bundle generation — re-scans only changed files using a SHA256 manifest. First run does a full scan and writes the manifest; subsequent runs detect changes, re-parse only dirty files, re-link, edge-diff, and write only dirty concept files.

| Option | Description |
|--------|-------------|
| `--force` | Full re-scan (same as `okf generate`) |
| `--enrich` | Re-enrich changed concepts with LLM (requires LLM config) |
| `--watch` | Continuous file watcher mode |
| `--debounce MS` | Watch mode debounce in milliseconds (default: 500) |
| `--exclude <dir>` | Skip directories matching this name (repeatable) |

**.okf-manifest.json** is stored in the bundle directory. It contains SHA256 content hashes per source file and edge hashes per concept. On missing/corrupt manifest, falls back to full scan.

---

## `okf lookup`

```bash
okf lookup [query] [options]
```

Search for concepts in a bundle.

| Option | Description |
|--------|-------------|
| `--bundle PATH` | Bundle directory (default: `./okf_bundle`) |
| `--file PATH` | Filter by source file |
| `--type TYPE` | Filter by concept type: `Function`, `Class`, `Module`, `Dependency` |
| `--tag TAG` | Filter by tag, repeatable (e.g. `--tag lang:python`) |
| `--limit N` | Max results (default: 10) |
| `--compact` | One-line output per result |
| `--json` | JSON output for programmatic use |
| `--full` | Raw `.md` file content |
| `--min-score N` | Minimum relevance score 0–1 (default: 0.1) |
| `--no-cache` | Bypass and skip writing the lookup cache |

---

## `okf diff`

```bash
okf diff <old_bundle> <new_bundle>
```

Compare two bundles — shows added, removed, and changed concepts.
Changes are detected via content hash (description, signature, tags).

| Option | Description |
|--------|-------------|
| `--compact` | One-line output per concept |
| `--json` | JSON output |

---

## `okf pairs`

```bash
okf pairs <bundle_dir> [output_file]
```

Convert bundle to JSONL training pairs.

**Environment variables:**

| Variable | Description |
|----------|-------------|
| `SKIP_SYNTH=1` | Static pairs only (no LLM) |
| `SYNTH_BASE_URL` | API endpoint |
| `SYNTH_API_KEY` | API key |
| `SYNTH_MODEL` | Model name |
| `MAX_WORKERS` | Parallel workers (default: 3) |
| `QA_PER_CONCEPT` | Q&A pairs per concept (default: 3) |
| `PAIR_TYPES` | Comma-separated: `codegen`, `qa`, `doc`, `summarize`, `crosslink` |

---

## `okf summarize`

```bash
okf summarize <bundle_dir>
```

Regenerate SUMMARY.md from an existing bundle (no re-scan).

---

## `okf agent`

```bash
okf agent [--bundle <path>] [--resume <session_id>]
```

Interactive REPL over an OKF bundle with persistent sessions and slash commands.

| Command | Description |
|---------|-------------|
| `/lookup <name>` | Full concept detail card |
| `/source <name>` | Show source code lines |
| `/calls [name]` | Show what this calls |
| `/called-by [name]` | Show what calls this |
| `/related [name]` | Show relationships |
| `/save` | Save session to disk |
| `/export [json\|md]` | Export session |
| `/sessions` | List saved sessions |
| `/resume <id>` | Resume a previous session |
| `/history` | Show conversation history |
| `/clear` | Clear context |

Sessions stored in `~/.okf/sessions/`. Requires LLM configured in `.okfconfig` for Q&A.

---

## `okf migrate`

```bash
okf migrate v0.1-to-v0.2 <bundle_dir> [--dry-run]
```

Convert OKF v0.1 bundles to v0.2 format in-place. Adds `okf_version`, `concept_id`, `language` to frontmatter and merges relationship sections. Use `--dry-run` to preview changes.

---

## `okf install`

```bash
okf install [agent] [agent ...]
```

Install integration for AI coding agents.

| Agent | What it does |
|-------|-------------|
| `claude` | Copies SKILL.md to Claude Code skills directory |
| `opencode` | Creates `.opencode/commands/lookup.md` |
| `copilot` | Creates `.github/copilot-instructions.md` |
| `cursor` | Creates `.cursorrules` |
| `windsurf` | Creates `.windsurfrules` |
| `cline` | Creates `.clinerules` |
| `all` | Runs all of the above |

---

## `okf visualize`

```bash
okf visualize <bundle_dir> [output.html]
```

Generate an interactive HTML explorer for an OKF bundle. Features:
- **Knowledge graph** — Cytoscape.js force-directed layout, color-coded by type
- **Concept detail panel** — signature, docstring, params, relationships, source code snippet
- **Source code viewer** — relevant lines from source file, Prism.js syntax highlighting
- **Parse tree viewer** — tree-sitter WASM-powered AST browser (Python, JS, TS, Go, Java, Ruby, Rust, C, C++, PHP)
- **Ego graph** — local neighborhood around any concept
- **Global graph** — full network overview with vis.js
- **Glass UI** — frosted glass cards, breathing gradient, theme toggle

Output is a self-contained HTML file (no server, no install).

---

## `okf serve`

```bash
okf serve [bundle_dir|git-url] [options]
```

Launch a local HTTP server for browsing an OKF bundle.

Supports **git repository URLs** — no manual clone needed:

```bash
# Local bundle
okf serve ./okf_bundle

# Git repo (clones to ~/.cache/okf/repos/, serves immediately)
okf serve https://github.com/user/repo.git@main

# Auto-generate bundle from source if missing
okf serve ./src --generate
okf serve https://github.com/user/repo.git@main --generate
```

When `--generate` is passed, runs `okf generate` on first clone (never on `--update`).
If the repo already has an `okf_bundle/` committed, generation is skipped.

| Option | Description |
|--------|-------------|
| `--port, -p PORT` | Port (default: 8000) |
| `--open, -o` | Open browser automatically |
| `--host HOST` | Host (default: 127.0.0.1) |
| `--stop` | Stop running server |
| `--update` | Fetch latest from git remote before serving |
| `--generate` | Auto-generate bundle if `okf_bundle/index.md` missing (first clone only) |
