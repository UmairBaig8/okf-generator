---
concept_id: rust/easy/lib/split_csv
description: Parses a comma-separated string into a vector of trimmed, non-empty strings.
language: rust
okf_version: '0.2'
resource: rust/easy/lib.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: split_csv
type: Function
---

# split_csv

Parses a comma-separated string into a vector of trimmed, non-empty strings.

## Signature

```rust
pub fn split_csv(line: &str) -> Vec<&str>
```

## Visibility

- `pub`

## Docstring

Parses a comma-separated string into a vector of trimmed, non-empty strings.

## Source
Lines 29–34 in `rust/easy/lib.rs`

```rs
pub fn split_csv(line: &str) -> Vec<&str> {
    line.split(',')
        .map(|s| s.trim())
        .filter(|s| !s.is_empty())
        .collect()
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [lib](/rust/easy/lib.md) |
