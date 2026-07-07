# okf-generator — Distribution Plan

## STATUS

| Channel | Status |
|---|---|
| PyPI v0.1.37 | ✅ live |
| GitHub repo + CI/CD | ✅ live |
| GitHub Pages landing + live viz | ✅ live |
| Docker (GHCR) | ✅ per release |
| MCP server | ✅ shipped |
| Agent integrations (×6) | ✅ shipped |
| One-liner install | ✅ `curl \| bash` |
| LICENSE / CoC / SECURITY / CONTRIBUTING | ✅ all present |
| Launch drafts (HN, Dev.to) | ✅ written |

## GAPS

### Tier 1 — Launch (highest leverage)

- [ ] **HN** — deploy `show-hn-draft.md` (Tue–Thu 8-10am ET, Option A title). Reply to every comment 1st 2h.
- [ ] **Dev.to** — publish `devto-draft.md`. Cross-post r/Python, r/MachineLearning.
- [ ] **Twitter/X** — thread demo GIF + 4 feature cards. Tag @anthropic @OpenAI @GitHubCopilot.
- [ ] **LinkedIn** — "Why I built a code knowledge graph generator" long-form post.
- [ ] **Reddit** — r/programming, r/Python, r/devops.

### Tier 2 — Infrastructure

- [ ] **MkDocs docs site** — searchable API reference + tutorial + FAQ.
- [ ] **Video demo** — 30-60s screen recording of generate + visualize. Embed on landing page.
- [ ] **Homebrew formula** — reach macOS dev audience.
- [ ] **GitHub Discussions** — enable (currently off). Q&A + show-and-tell.
- [ ] **Landing page analytics** — Plausible or Vercel.

### Tier 3 — Content & SEO

- [ ] Blog: "How to set up OKF for your project"
- [ ] Blog: "RAG vs OKF: when exact symbol lookup wins"
- [ ] Social preview tags on landing page (og:image, structured data)

### Tier 4 — Polish

- [ ] PyPI classifier `3 - Alpha` → `4 - Beta` (after next release)
- [ ] `.devcontainer/` for VS Code Remote
- [ ] Discord or GH Discussion for parser roadmap voting

## 30-DAY SPRINT

```
Week 1: HN + Dev.to + Twitter launch (existing drafts)
Week 2: Publish 2 blog posts + video demo
Week 3: Homebrew + GH Discussions + MkDocs site
Week 4: Analytics review, respond to issues, tag v0.2.0
```
