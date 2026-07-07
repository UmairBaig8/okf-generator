# okf-generator — Launch & Growth Plan

> Created: 2026-07-07  
> Version at time of writing: v0.1.37  
> Status: ready to launch — CI green, PyPI live, landing page fresh

---

## Current State

| Area | Status |
|---|---|
| PyPI | ✅ v0.1.37 published |
| CI/CD | ✅ publish.yml auto-releases on tag push |
| Landing page | ✅ redesigned (open-design.ai style) |
| Languages | ✅ 13 (Python, JS, TS, Go, Java, Rust, Ruby, C, C++, C#, SQL, PHP, Dart, Scala, Julia + planned more) |
| Manifest formats | ✅ 17 |
| MCP server | ✅ `okf mcp` |
| Agent installs | ✅ claude / cursor / copilot / windsurf / cline / opencode |
| Interactive viz | ✅ `okf visualize` |
| Show HN draft | ✅ `show-hn-draft.md` (90% ready) |
| Dev.to draft | ✅ `devto-draft.md` (90% ready) |
| Failing tests | ⚠️ 3 config tests fail due to user-level `~/.config/okf/config.json` leaking into tests |
| README language count | ⚠️ says "10 languages" in some places — needs update to 13 |

---

## Blockers to Fix Before Any Public Post

### 1. Fix 3 failing config tests

**Problem:** `test_okf_config_loads_defaults`, `test_okf_config_env_var_overrides_file`, and `test_okf_config_dump_and_read` fail because the user-level `~/.config/okf/config.json` bleeds into test isolation. Someone running `pytest` from HN will see 3 failures.

**Fix:** In each of the 3 tests, also null out `CONFIG_FILES[1]` (the user config path) inside the `try` block, mirroring the pattern already used in `test_okf_config_dump_and_read` for `CONFIG_FILES[0]`.

```python
import okf.config as cfgmod
orig0, orig1 = cfgmod.CONFIG_FILES[0], cfgmod.CONFIG_FILES[1]
cfgmod.CONFIG_FILES[0] = Path("/nonexistent/path")
cfgmod.CONFIG_FILES[1] = Path("/nonexistent/path")
try:
    cfg = load()
    # ... assertions
finally:
    cfgmod.CONFIG_FILES[0] = orig0
    cfgmod.CONFIG_FILES[1] = orig1
```

### 2. Update language count in README

Search README.md and docs/index.html for "10 languages" and update to "13 languages". The language table in README also needs PHP, Dart, Scala, and Julia rows added.

### 3. Update Show HN draft

- Change "10 languages" → "13 languages"
- Add one sentence about the MCP server: *"It now supports 13 languages and ships an MCP server, so Claude Desktop / Cursor can query the bundle directly."*

---

## Tier 1 — This Week (Do First)

### Action 1: Show HN post

**Why first:** HN is where developer tools get initial traction. A single front-page Show HN feeds Reddit threads, blog citations, and GitHub star spikes simultaneously.

**When to post:** Tuesday–Thursday, 7–9 AM US Eastern (12:30–2:30 PM IST). Never weekends or Monday.

**Title (use this exactly):**
```
Show HN: okf-generator – turn any codebase into an agent-readable knowledge graph
```

**Post body (final version of `show-hn-draft.md` after updates):**

```
I built this because I was indexing a large multi-domain codebase (Python
data connectors, ML pipelines, SQL schemas) and kept hitting the same wall:
giving an AI agent the whole repo as context is slow and burns tokens. Local
SLMs (Gemma, Llama, Phi) on a laptop just run out of memory entirely.

okf-generator scans a repo with tree-sitter AST parsers and writes one
markdown file per function, class, module, and dependency — cross-referenced
(calls, called-by, imports). It now supports 13 languages and ships an MCP
server so Claude Desktop / Cursor can query the bundle directly.

Instead of an agent reading a 600-line file to find one method (~14,000
tokens), it runs:

  okf lookup WorldBankConnector

and gets back ~140 tokens of exact, typed context:

  CLASS: WorldBankConnector
  Source    : connectors/economic_data.py  line 51
  Methods   : get_indicator, search
  Called by : DataPipeline.fetch_economic

A few specifics:
- Extraction is fully deterministic and offline — no LLM call unless you
  explicitly turn on enrichment (works with any OpenAI-compatible endpoint,
  including local llama.cpp/Ollama).
- 13 languages, 17 manifest formats (pip, npm, cargo, go.mod, maven, etc.)
- MCP server: okf mcp ./okf_bundle — any Claude Desktop/Cursor setup can
  query the bundle directly.
- One-command agent wiring: okf install claude / cursor / copilot / windsurf
- Interactive HTML viz (self-contained, no server): okf visualize ./bundle

GitHub: https://github.com/UmairBaig8/okf-generator
pip install okf-generator
```

**Rules for the HN thread:**
- Reply to every comment within the first 2 hours
- Don't argue — thank people who critique, acknowledge valid points
- Don't post any other content on HN the same day
- If someone asks for a feature, say "good idea, opening an issue"

---

### Action 2: Dev.to article

**File:** `devto-draft.md` (already ~80% written)

**Final steps before publishing:**
1. Add the before/after image: `![before/after](https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/docs/images/before_after.svg)`
2. Add a "Getting started in 60 seconds" section with the 3-command flow
3. Add a "MCP server setup" section (this is new since the draft was written)
4. Publish with tags: `ai`, `opensource`, `python`, `productivity`
5. Set cover image to the banner PNG (already the cover_image in frontmatter)

**Title:** `Stop feeding your AI agent the whole codebase`

**Estimated read time:** 6–8 minutes — ideal for Dev.to

**Post on the same day as Show HN** or the day after to capture the traffic wave.

---

### Action 3: Reddit — r/LocalLLaMA

This is the highest-value community for this tool. Local SLM users feel the pain of context overflow every day.

**Title:**
```
I built a tool that makes local Gemma/Llama actually usable on large codebases — no RAG, no embeddings
```

**Body structure:**
1. The problem: local models run out of context on real repos
2. The solution: exact symbol lookup instead of whole-file reads
3. Show the terminal output (the before/after)
4. Link: GitHub + `pip install okf-generator`
5. Mention MCP server for people using Continue.dev or local agent setups

**Rules:** Don't cross-post the exact same text. r/LocalLLaMA has seen enough "I built a thing" posts — lead with the problem, show the output, let the code speak.

**Other subreddits to post in the same week (different angles):**

| Subreddit | Angle | Title |
|---|---|---|
| r/Python | CLI tool, pip install, tree-sitter | `okf-generator: tree-sitter powered code indexer for AI agents` |
| r/programming | Architecture (AST → knowledge graph) | `How I turn a codebase into a queryable knowledge graph` |
| r/MachineLearning | Token efficiency for local SLMs | `100x token reduction for local LLM code tasks — no vector DB needed` |
| r/ClaudeAI | Claude Code integration | `okf install claude wires your entire codebase into Claude Code` |
| r/cursor | Cursor integration | `okf install cursor — instant codebase knowledge for Cursor` |

Space these out — don't post to all subreddits on the same day.

---

### Action 4: Twitter/X thread

**Tweet 1 (the hook):**
```
Your AI agent re-reads 600 lines every time it touches a function.
That's ~14,000 tokens just to find one method signature.

I built okf-generator to fix this. 🧵
```

**Tweet 2 (the solution):**
```
okf-generator scans your repo with tree-sitter AST parsers.

Every function, class, module, and dependency becomes a structured
markdown file — cross-referenced by calls and imports.

Then your agent runs:

  okf lookup WorldBankConnector

→ 140 tokens. Exact answer. No re-reading.
```

**Tweet 3 (the CTA):**
```
13 languages. 17 manifest formats. MCP server included.
Works with Claude Code, Cursor, Copilot, Windsurf, Cline.

pip install okf-generator
okf install all

↓ GitHub (MIT)
https://github.com/UmairBaig8/okf-generator
```

**Who to tag:** Tag 2–3 people active in the AI tooling/local LLM space. Don't tag people randomly — only if the tool is genuinely relevant to what they post about.

---

## Tier 2 — Within 2 Weeks

### Action 5: Product Hunt launch

Product Hunt works when you prepare. A cold launch with no hunters or pre-built following gets buried.

**Prep checklist (do before launch day):**

- [ ] Write tagline: *"Map any codebase into an agent-readable knowledge graph — zero LLM required"*
- [ ] Prepare 4 screenshots:
  1. Terminal output of `okf lookup WorldBankConnector`
  2. The interactive HTML visualization
  3. The before/after token comparison diagram (`docs/images/before_after.svg`)
  4. The agent install grid (6 agents, one command each)
- [ ] Write the "first comment" — post it yourself immediately after launch explaining the MCP angle and local SLM story
- [ ] Find a hunter — post in the Show HN thread asking if anyone with PH followers wants to hunt it, or ask in AI developer Discord communities

**Launch day:**
- Launch on **Tuesday or Wednesday** (highest PH traffic days)
- Be online the entire day to reply to comments
- Post the PH link on Twitter/X and in relevant Discord servers

---

### Action 6: Awesome list PRs

These are permanent wins — they drive organic discovery indefinitely.

**Target lists (open PRs to each):**

| List | Repo | Section |
|---|---|---|
| awesome-mcp-servers | github.com/punkpeye/awesome-mcp-servers | Code Intelligence |
| awesome-claude-code | github.com/hesreallyhim/awesome-claude-code | Skills / Tools |
| awesome-python | github.com/vinta/awesome-python | Code Analysis |
| awesome-ai-tools | github.com/mahseema/awesome-ai-tools | Developer Tools |
| awesome-llm-tools | search for current maintained list | Code tools |

**PR description template:**
```
Add okf-generator — turns any codebase into an agent-readable knowledge
graph using tree-sitter AST parsers. Zero-LLM extraction, 13 languages,
MCP server included. MIT licensed.
https://github.com/UmairBaig8/okf-generator
```

Keep PRs small — one tool, correct section, matching the repo's existing format exactly.

---

### Action 7: GitHub repo optimization

These cost nothing and permanently improve discoverability:

- [ ] Add topics to the repo: `knowledge-graph`, `code-intelligence`, `mcp`, `tree-sitter`, `llm-tools`, `local-llm`, `ai-agents`, `code-indexing`
- [ ] Update the repo description to: *"Map any codebase into an agent-readable knowledge graph — 13 languages, MCP server, zero LLM required"*
- [ ] Add a social preview image (Settings → Social preview → upload `docs/images/social_preview.png`)
- [ ] Add `CITATION.cff` file for researchers who want to cite the tool
- [ ] Make sure the website field in the repo header points to `https://umairbaig8.github.io/okf-generator/`

---

## Tier 3 — Within 1 Month

### Action 8: Long-form blog post

A deep technical post travels further than a Show HN announcement because it gets shared in newsletters.

**Title option A:** `How I cut AI agent token costs by 100x without RAG`  
**Title option B:** `Building a code knowledge graph with tree-sitter: architecture and lessons`

**Outline:**
1. The problem (agents re-reading files, local SLM memory limits)
2. Why RAG doesn't solve it (approximate, needs embedding infra)
3. The approach: AST → structured concepts → exact lookup
4. The linker: how cross-references are resolved across languages
5. MCP integration: what it enables
6. Benchmark: 14,000 tokens → 140 tokens, real example
7. What's next (more languages, incremental regen, web dashboard)

**Where to publish:**
- Your own GitHub Pages blog (simplest — just push a markdown file)
- Hashnode (free, good SEO, developer audience)
- Medium (lower organic reach now but still has a Python/AI readership)

**After publishing:** Submit to these newsletters as a community link:
- [TLDR AI](https://tldr.tech/ai) — submit at tldr.tech/ai/contribute
- [The Rundown AI](https://www.therundown.ai/) — community submissions
- [Latent Space](https://www.latent.space/) — DM @swyx or @aipodcast on Twitter

---

### Action 9: Discord / Slack communities

Post in these communities once the Show HN is up (link to HN thread, don't cross-post the same pitch):

| Community | Channel | Angle |
|---|---|---|
| Anthropic Discord | #tools / #claude-code | `okf install claude` integration |
| OpenCode Discord | general | `/lookup` command integration |
| Latent Space Discord | #tools | Technical architecture angle |
| LangChain Discord | #show-and-tell | MCP server, knowledge graph |
| Hugging Face Discord | #llm-tools | Local SLM angle |
| MLOps Community Slack | #tools | CI/CD bundle workflow |

**Rule:** Be a real community member, not a one-shot promoter. Participate in other threads before posting your own.

---

### Action 10: AI newsletter outreach

After the blog post is written, email these newsletters directly:

| Newsletter | Audience | Submit |
|---|---|---|
| TLDR AI (~500k subs) | ML engineers, AI practitioners | tldr.tech/ai/contribute |
| The Batch (deeplearning.ai) | ML community | community section on site |
| Pointer (programmers) | Senior devs | pointer.io — reply to any issue |
| Console (dev tools) | Developer tools specifically | console.dev/tools |

Console.dev is the highest-leverage one — it specifically covers developer tools and their audience is exactly who will use okf-generator.

---

## Content Calendar (Suggested Sequence)

| Day | Action | Platform |
|---|---|---|
| Day 0 (prep) | Fix 3 failing tests, update README language count, finalize Show HN draft | Local |
| Day 1 (Tue/Wed/Thu morning) | Post Show HN | Hacker News |
| Day 1 (afternoon) | Post thread | Twitter/X |
| Day 2 | Post Dev.to article | Dev.to |
| Day 3 | Post r/LocalLLaMA | Reddit |
| Day 4 | Post r/Python | Reddit |
| Day 5 | Post r/programming | Reddit |
| Week 2 | Open awesome-list PRs | GitHub |
| Week 2 | Optimize GitHub repo topics/description | GitHub |
| Week 2–3 | Product Hunt prep (screenshots, hunter search) | — |
| Week 3 | Product Hunt launch | Product Hunt |
| Week 3–4 | Write long-form blog post | Hashnode / personal |
| Month 2 | Submit blog post to newsletters | Email outreach |
| Ongoing | Engage Discord communities | Discord/Slack |

---

## What Success Looks Like

| Timeframe | Realistic target |
|---|---|
| Day 1 (Show HN) | 50–150 GitHub stars, front page or Ask HN second page |
| Week 1 | 200–400 stars, first organic forks |
| Month 1 | 500–1,000 stars, PyPI downloads visible in stats |
| Month 3 | Listed on 3+ awesome lists, 1,000+ stars, regular issues/PRs from strangers |

The product is genuinely good. The gap is purely distribution — nobody knows it exists yet. One good Show HN post changes that.

---

## Notes

- **Don't buy followers, stars, or upvotes.** HN and Reddit have good spam detection and it would destroy credibility.
- **Respond to every issue and PR.** First impressions matter. A tool that replies fast keeps contributors.
- **Track what works.** Check GitHub traffic (`/graphs/traffic`) and PyPI stats weekly. Double down on whatever channel drives the most installs.
- **Version cadence:** Keep shipping. A repo that releases every 1–2 weeks looks alive. Dead repos lose stars.
