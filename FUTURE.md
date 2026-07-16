# Future Plans

Ordered by **impact**, not effort. Items at the top deliver the most value per build hour.

---

## ~~1. CI/CD Realworld Bundle Auto-Publish~~ ✅ Done (v0.1.44)

Extended `.github/workflows/demo-viz.yml` to generate `docs/okf_bundle/` from `tests/fixtures/realworld/` on every push to `main`. Added bundle verification (≥10 concept files). Landing page "Try it live" section now has a "Live Bundle" link. Updated `.gitignore` to un-ignore `docs/okf_bundle/`.

---

## ~~2. User-Facing Auto-Bundle Template~~ ✅ Done (v0.1.44)

Created `docs/examples/okf-auto-bundle.yml` — a ready-to-copy workflow. Updated `docs/user-guide/ci-cd.md` with the full template and explanation. Updated README link to point to new CI/CD doc.

---

## ~~3. v0.2 Schema Bump~~ ✅ Done (v0.1.44)

Bumped `"0.1"` → `"0.2"` in all generator emission points. Added `okf_version`, `concept_id`, `language`, `status` to every concept frontmatter. Merged relationship sections into a single `## Relationships` table with typed edges. Created `okf migrate v0.1-to-v0.2`.

---

## ~~4. `okf agent` REPL~~ ✅ Done (v0.1.44)

Interactive REPL with slash commands, persistent sessions, LLM-powered Q&A.

---

## ~~5. Tree-sitter WASM in Viz~~ ✅ Done (v0.1.44)

Interactive AST browser in the visualization — click any concept, switch to Parse Tree, see the full tree-sitter parse tree with collapsible scopes.

---

## ~~6. LSP Enrichment~~ ✅ Done (v0.1.48)

Compiler-accurate caller/callee resolution via local language servers. 4 servers mapped: pyright, gopls, rust-analyzer, typescript-language-server. `okf lsp status|resolve|map` subcommands. New `okf/enrich/` package with pluggable Enricher contract.

---

## ~~1. Incremental Generation (`okf update`)~~ ✅ Done (v0.1.49)

**Impact:** Very High  
**Effort:** Medium (3–5 days)

Store SHA256 manifest per source file + per-concept edge hash. On `okf update`, diff source tree, re-parse only changed files, full re-link, edge-diff to find dirty concepts, write only changed `.md` + indexes + SUMMARY.md + manifest last. Watch mode via `watchdog.Observer`.

```
okf update                          # incremental
okf update --force                  # full re-scan
okf update --watch                  # watch mode (500ms debounce)
okf update --exclude tests          # respect exclude patterns
```

**New files:** `okf/manifest.py`, `okf/update.py`, `okf/watcher.py`  
**Modified:** `okf/cli.py`, `okf/config.py`, `pyproject.toml`  
**Tests:** 12 in `tests/test_update.py` — equivalence (edit/rename/delete), edge cascade, orphan cleanup, force, corrupt manifest, relink stability. All 313 pass.

**Known limitations:**
- `--enrich` flag is CLI-wired but LSP/LLM enrichment not integrated into the update pipeline yet
- `--watch` debounce from `.okfconfig` loaded but not wired to watcher (hardcoded 500ms)
- Benchmark fixtures deferred

---

## 2. Configurable LSP Providers

**Impact:** High  
**Effort:** Low (1 day)

**Problem:** `_lsp_map.py` is hardcoded. Users who want a different LSP server (e.g. `sqllens-language-server` for SQL, `jdtls` for Java) must edit source or wait for a release.

**Solution:** Add a `lsp.servers` section to `.okfconfig`:

```json
{
  "lsp": {
    "servers": {
      ".sql": ["sqllens-language-server", "--stdio"],
      ".java": ["jdtls"]
    }
  }
}
```

User-supplied entries override `_lsp_map.py`. No code changes needed for new servers.

**Design:**
- `okf/enrich/_lsp_map.py` loads config, merges with built-in map, user entries take precedence
- `okf lsp map` shows merged result (built-in + config)
- `okf lsp status` uses merged map

**What it unlocks:** Community can add any LSP server without a PR. Lowers the bar for SQL, Java, Lua, Elixir, etc.

---

## 3. Bundle Validation (`okf validate`)

**Impact:** High  
**Effort:** Low (1–2 days)

**Problem:** No built-in way to verify bundle integrity. Broken links, orphaned concepts, malformed timestamps, and spec non-conformance go undetected until an AI agent or consumer fails to resolve a reference.

**Solution:** `okf validate` command that checks:

| Check | Description |
|-------|-------------|
| Spec conformance | Every `.md` has parseable frontmatter with non-empty `type`. Reserved files (`index.md`, `log.md`) follow spec structure. |
| Link resolution | All markdown links resolve to existing concept files in the bundle. |
| Orphan detection | Concepts with zero inbound links from other concepts (configurable threshold). |
| Timestamp format | All `timestamp` values are valid ISO 8601. |
| Cross-reference integrity | `calls` / `called_by` / `related` edges point to existing concept IDs. |
| Duplicate concept IDs | No two concepts share the same `concept_id`. |

```
okf validate                         # validate ./okf_bundle (default)
okf validate --bundle ./path         # explicit path
okf validate --strict                # warnings → exit code 1
okf validate --no-orphans            # skip orphan check
okf validate --fix                   # auto-fix trivial issues (trailing whitespace, missing newline)
```

**Design:** Iterates bundle `.md` files, parses frontmatter, resolves links against file tree, checks edge targets against concept index. Each check is an independent pass — failures in one don't block others. Exit codes: 0 (pass), 1 (errors), 2 (warnings with `--strict`).

**What it unlocks:** CI integration for bundle quality gates. Teams can enforce spec compliance and link hygiene before merging bundle changes. Makes the bundle self-auditing.

---

## 4. Semantic + Graph Search

**Impact:** High  
**Effort:** Medium (3–5 days)

**Problem:** Current lookup is keyword/token-based. "find payment validation" returns concepts containing "payment" or "validation" but can't answer "what validates payments?" — that requires graph traversal.

**Solution:** Three-tier search:

1. **Keyword** (existing) — exact title/description match
2. **Graph** — traverse edges: caller → callee → related → semantic related
3. **Vector** (optional) — embed concept descriptions, nearest-neighbor search

```
okf lookup "what validates payments?"
-> concept: validate_payment()
   path: calls -> PaymentValidator
   path: related -> PaymentDTO
   path: called_by -> PaymentController.charge
```

**Design:** Graph queries on the existing `calls`, `called_by`, `related`, `related_semantic` edges. Vector search via a small local embedding model (or skip if no model available). Results show the graph path, not just the node.

**What it unlocks:** AI agents can navigate the bundle like a knowledge graph, not just a document store. "Find the impact of changing X" becomes a graph query.

---

## 5. Infrastructure / Domain Manifest Scanners

**Impact:** Medium–High  
**Effort:** Low–Medium (1–3 days per scanner)

**Problem:** Most scanner requests aren't for new languages — they're for config/infrastructure formats that carry operational knowledge. Crossplane (already done), Kubernetes manifests, Terraform, OpenAPI, Docker Compose are more valuable to users than adding Scala v2 syntax support.

**Priority order:**

| Scanner | Effort | Why now |
|---------|--------|---------|
| **OpenAPI / Swagger** | 1 day | YAML parser already exists. Extract endpoints, request/response schemas, auth flows as concepts. Links to code via route handler names. |
| **Kubernetes manifests** | 1 day | YAML parser exists. Extract Deployments, Services, ConfigMaps, CRDs. Links to container images. |
| **Terraform / OpenTofu** | 2 days | HCL parser needed (tree-sitter-hcl exists). Extract resources, data sources, variables, outputs. Links to cloud provider docs. |
| **Docker Compose** | 0.5 day | YAML parser exists. Extract services, networks, volumes, env vars. |
| **CI/CD workflows** | 1 day | YAML parser exists. Extract jobs, steps, triggers from GitHub Actions / GitLab CI. Links to scripts. |

Design mirrors the Crossplane domain pattern: YAML-based manifests → domain classifier → concept extraction. Each gets a rule file in `okf/domains/rules/`.

**What it unlocks:** OKF becomes useful for platform teams, not just application developers. A bundle can describe the full deployment graph, not just the source code.

---

## 6. Microservice Architecture Awareness

**Impact:** Very High  
**Effort:** Ongoing (builds on domain engine + multi-repo linking)

**Problem:** OKF today understands a single codebase. Real architecture lives across microservices — shared libraries, service boundaries, API contracts, event buses, Kafka topics with producers/consumers, cross-service data flows. An agent that only sees one repo at a time can't reason about the system.

**Phased approach:**

| Phase | What | How |
|-------|------|-----|
| **Phase 1 — Shared libs** | Already works. Index the common library dir and the linker resolves cross-references. | `okf generate ./shared-lib` |
| **Phase 2 — Multi-repo bundles** | Point at multiple source roots, get a single merged bundle with cross-service edges. Linker resolves by symbol name. | `okf generate ./service-a ./service-b ./shared-lib` |
| **Phase 3 — Service boundaries** | New concept type `Service` with detected boundaries (API surface, deps on other services). Inferred from directory structure + manifest deps. | Domain rules |
| **Phase 4 — Event/message topology** | Kafka, RabbitMQ, SQS — topic/exchange nodes linked to their producers and consumers. Domain rule files parse producer/consumer configs. | `okf/domains/rules/kafka.yaml` |
| **Phase 5 — Data flow graphs** | Trace data lineage across service boundaries: "Service A writes to this topic → Service B reads it → Service C transforms → DB." Agent navigable. | Graph query on merged bundle |

**Design:** Extends the domain classification engine (`okf/domains/engine.py`). Each phase adds rule files, not core changes. The multi-repo merger reuses the existing linker — just feed it concepts from multiple source roots.

**What it unlocks:** An agent that understands architecture, not just files. "Trace this Kafka topic from producer to consumer," "what services depend on this shared library?", "which endpoints does Service A expose to Service B?" — all answerable without reading a dozen repos.

**Impact:** Medium  
**Effort:** Low (1–2 days)

**Problem:** Running `okf generate` overwrites the bundle. No history, no rollback, no incremental comparison.

**Solution:** Store versions in `okf_bundle/versions/.manifest.json`:

```
okf_bundle/
├── current/              # symlink to latest version
├── versions/
│   ├── v2026-07-14-1/
│   ├── v2026-07-14-2/
│   └── .manifest.json    # version log
└── SUMMARY.md
```

```bash
okf generate --keep          # keep previous version
okf diff ./bundle            # diff current vs previous
okf diff ./bundle v1 v2      # diff two stored versions
okf rollback ./bundle        # restore previous
```

Design builds on existing `okf diff` command — just add directory-level versioning.

**What it unlocks:** CI pipelines can detect knowledge drift. "This PR added 3 new endpoints and deprecated 2 others" without reading any code.

---

## ~~7. MkDocs Replacement / Static Site Generator~~ ⏳ Deferred

**Impact:** Low  
**Effort:** Medium (3–5 days)

Current docs-site is functional. The nested `docs-site/docs-site/` path issue was fixed in v0.1.48. Remaining issue: build times with 1000+ bundle `.md` files. Deferred until it becomes a bottleneck.

Options if revisited:
- **MkDocs config fix** — adjust `site_url`, exclude `okf_bundle/` from nav
- **mdBook** — single Rust binary, no Python deps
- **Plain HTML** — custom build script, full control

---

## 8. SAST Enrichment (`okf enrich --sast`)

**Impact:** Medium  
**Effort:** Low (1–2 days)

Wrap deterministic SAST tools (semgrep, bandit, gosec) in the same `Enricher` contract used by LSP and LLM. Each tool becomes a `SastEnricher(Enricher)` with `start/run/stop` lifecycle. Structured CWE/severity output injected into concept frontmatter alongside LSP call graphs and LLM summaries.

**Why:** LSP resolves *what* calls *what*. SAST resolves *which constructs* are *vulnerable*. Combined: compiler-accurate call graphs + deterministic security findings + LLM behavioural summaries — three orthogonal passes, one pipeline.

**Design:** `okf/enrich/_sast_map.py` (ext → tool config), `okf/enrich/sast.py` (subprocess runner, semgrep JSON → concept mapping, CWE→severity table). `okf enrich --sast` flag.

---

## 9. IDE Plugins

**Impact:** Medium  
**Effort:** Very High (2–4 weeks each)

**VS Code extension:** Reads `.okf_bundle/` from workspace root. Shows hover tooltips with docstrings/signatures, call-graph peek, jump-to-def across languages. Uses bundle's cross-reference data (no language server needed).

**JetBrains plugin:** Same concept via IntelliJ plugin SDK.

**What it unlocks:** OKF becomes invisible — developers get codebase-wide context without leaving their editor. Makes the bundle useful for humans, not just AI agents.

---

## 10. Native SDKs (Python, Node, Go)

**Impact:** Low–Medium  
**Effort:** Medium (3–5 days per SDK)

**Problem:** Consuming OKF bundles currently requires shelling out to the `okf` CLI or using the MCP server. Programmatic consumption needs a library.

**SDK surface:**
```python
# Python (already largely exists via okf.pairs/Python API)
from okf import load_bundle, search
concepts = load_bundle("./okf_bundle")
results = search(concepts, "payment")
```

**Node / Go SDKs:** Thin wrappers over the bundle `.md` file format. Parse frontmatter, expose search, filter by type/tag. No duplicate parsing logic — just a reader library.

**What it unlocks:** Integration into custom tooling (code review bots, dashboards, CI checks) without shelling out.
