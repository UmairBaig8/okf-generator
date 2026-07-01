# OKF Knowledge Bundle — Copilot Instructions

This project uses `okf-generator` to produce an OKF v0.1 knowledge bundle at `./okf_bundle/`. The bundle contains structured markdown files — one per function, class, module, and dependency — that Copilot can read for precise context instead of scanning entire files.

## Before editing a function or class

Always look it up first to get its signature, parameters, docstring, and dependencies:

```bash
okf lookup --bundle ./okf_bundle <ConceptName>
```

## Finding all concepts from a module

```bash
okf lookup --bundle ./okf_bundle --file path/to/source.py
```

## Filtering by concept type

```bash
okf lookup --bundle ./okf_bundle --type Class
okf lookup --bundle ./okf_bundle --type Function
okf lookup --bundle ./okf_bundle --type Dependency
```

## Filtering by language or ecosystem

```bash
okf lookup --bundle ./okf_bundle --tag lang:python
okf lookup --bundle ./okf_bundle --tag lang:typescript
okf lookup --bundle ./okf_bundle --tag ecosystem:pip
okf lookup --bundle ./okf_bundle --tag ecosystem:npm
```

## Getting JSON for programmatic use

```bash
okf lookup --bundle ./okf_bundle --json <ConceptName>
```

## Checking dependencies

```bash
# All dependencies
okf lookup --bundle ./okf_bundle --type Dependency

# Dependencies for a specific ecosystem
okf lookup --bundle ./okf_bundle --type Dependency --tag ecosystem:pip

# Dev dependencies
okf lookup --bundle ./okf_bundle --type Dependency --compact | grep Dev
```

## Seeing what changed between bundles

```bash
okf diff ./okf_bundle.bak ./okf_bundle --compact
```

## Bundle location

- Default: `./okf_bundle/`
- Also checked: `./Knowlege/okf_bundle/`, `./knowledge/okf_bundle/`
- [okf-generator README](../README.md)
