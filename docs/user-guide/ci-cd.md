# CI/CD & Cloud Integration

Because `okf generate` is fully offline and deterministic, it fits naturally into automated pipelines and serverless infrastructure.

## GitHub Actions — One-Click Setup

Copy this ready-made workflow into your repo to auto-generate and commit an OKF bundle on every push:

```yaml
# .github/workflows/okf-auto-bundle.yml
# Full file: docs/examples/okf-auto-bundle.yml
name: OKF Auto-Bundle

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Install Rust
        run: rustup show || curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
      - name: Install okf-generator
        run: pip install okf-generator
      - name: Generate OKF bundle
        run: |
          okf generate ./src ./okf_bundle
          echo "Concepts: $(find okf_bundle -name '*.md' | wc -l)"
      - name: Commit bundle
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: update OKF bundle [skip ci]"
          file_pattern: okf_bundle/
          commit_user_name: okf-bot
          commit_user_email: bot@okf.dev
```

Customize `okf generate ./src ./okf_bundle` to match your source directory. Add `--enrich deep` if you have an LLM configured.

> 📄 **Ready-to-copy template:** [`docs/examples/okf-auto-bundle.yml`](https://github.com/UmairBaig8/okf-generator/blob/main/docs/examples/okf-auto-bundle.yml)

### How it works

1. **On push to `main`** — the workflow runs `okf generate` on your source code
2. **Bundle is committed** — `okf_bundle/` gets updated in your repo
3. **AI agents see it** — Claude Code, Cursor, Copilot, and OpenCode auto-detect the bundle and use it for context
4. **Zero maintenance** — no manual re-generation, no server to run

## Serverless / Cloud Storage

Push the bundle to cloud storage for centralized multi-tenant access:

```bash
# Generate
okf generate ./src ./okf_bundle

# Sync to S3 (or GCS, Azure Blob)
aws s3 sync ./okf_bundle s3://my-org-okf-bundles/my-project/ \
  --delete \
  --cache-control "max-age=3600"
```

### S3 Static Hosting

Configure the S3 bucket for static website hosting, then teams can browse bundles without any server:

```bash
# Enable static hosting
aws s3 website s3://my-org-okf-bundles \
  --index-document index.html \
  --error-document error.html

# Set CORS for multi-origin access
aws s3api put-bucket-cors --bucket my-org-okf-bundles \
  --cors-configuration '{
    "CORSRules": [{
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET"],
      "AllowedHeaders": ["*"]
    }]
  }'
```

### Multi-Project Monorepo

For monorepos with many services:

```bash
# Index each service independently
for dir in services/*/; do
  name=$(basename "$dir")
  okf generate "$dir" "./okf_bundles/$name"
done

# Upload all bundles
aws s3 sync ./okf_bundles s3://my-org-okf-bundles/
```

## GitLab CI

```yaml
okf-bundle:
  image: python:3.11-slim
  script:
    - pip install okf-generator
    - okf generate ./src ./okf_bundle
  artifacts:
    paths:
      - okf_bundle/
```

## Pre-commit Hook

Generate a minimal bundle on every commit to keep it fresh:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: okf-generate
        name: OKF bundle regeneration
        entry: okf generate . ./okf_bundle
        language: system
        pass_filenames: false
        files: \.(py|js|ts|go|java|rs|rb|c|cpp|cs|sql|swift|kt)$
        stages: [pre-commit]
```

Run `pre-commit install` to activate. The hook only triggers when source files change.

## Tips

- **Speed**: First run scans everything; subsequent runs only re-scan changed files (mtime-based).
- **CI cost**: Bundle generation takes seconds for most projects — negligible CI time.
- **Branch isolation**: Use branch-based S3 paths (`s3://bundles/$BRANCH/`) for PR previews.
- **Cache**: The lookup cache is auto-generated; include it in your bundle for faster agent lookups.
