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

Scans a source directory and produces an OKF v0.1 knowledge bundle.

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

Generate an interactive HTML graph of an OKF bundle. Uses D3.js force-directed graph with:
- Color-coded nodes by concept type (Class, Function, Module, Dependency, etc.)
- Relationship edges (calls, called-by, imports, related)
- Search/filter by name
- Tooltip on hover showing description and resource
- Pan/zoom

Output is a self-contained HTML file (no server, no install).

---

## `okf serve`

```bash
okf serve [bundle_dir] [options]
```

Launch a local HTTP server for browsing an OKF bundle.

| Option | Description |
|--------|-------------|
| `--port, -p PORT` | Port (default: 8000) |
| `--open, -o` | Open browser automatically |
| `--quiet, -q` | Suppress request logs |
| `--host HOST` | Host (default: 127.0.0.1) |
