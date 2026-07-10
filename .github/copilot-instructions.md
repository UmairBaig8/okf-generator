# OKF Knowledge Bundle — Copilot Instructions

## CRITICAL RULE: Never read source files directly for context

This project uses `okf-generator` to produce an OKF v0.2 knowledge bundle at `./okf_bundle/`. The bundle contains structured markdown files — one per function, class, module, and dependency.

**BEFORE reading or editing any source file, you MUST run:**

```bash
okf lookup --bundle ./okf_bundle <ConceptName>
```

This returns signature, parameters, docstring, dependencies, callers, and callees in milliseconds — faster and more accurate than reading the source file.

## Common lookups

```bash
# Single concept full detail
okf lookup --bundle ./okf_bundle ClassName

# All concepts from one source file
okf lookup --bundle ./okf_bundle --file path/to/source.py

# Filter by type
okf lookup --bundle ./okf_bundle --type Class
okf lookup --bundle ./okf_bundle --type Function
okf lookup --bundle ./okf_bundle --type Dependency

# Filter by language
okf lookup --bundle ./okf_bundle --tag lang:python
okf lookup --bundle ./okf_bundle --tag lang:typescript
okf lookup --bundle ./okf_bundle --tag lang:go

# Filter by ecosystem
okf lookup --bundle ./okf_bundle --tag ecosystem:pip
okf lookup --bundle ./okf_bundle --tag ecosystem:npm
okf lookup --bundle ./okf_bundle --tag ecosystem:cargo

# JSON output for programmatic use
okf lookup --bundle ./okf_bundle --json <Name>

# Dependencies (all or by ecosystem)
okf lookup --bundle ./okf_bundle --type Dependency
okf lookup --bundle ./okf_bundle --type Dependency --tag ecosystem:pip --compact
```

## Seeing what changed between bundles

```bash
okf diff ./okf_bundle.bak ./okf_bundle --compact
okf diff ./okf_bundle.bak ./okf_bundle --json
```

## Bundle location

- Default: `./okf_bundle/`
- Also checked: `./Knowlege/okf_bundle/`, `./knowledge/okf_bundle/`
- [okf-generator README](../README.md)
