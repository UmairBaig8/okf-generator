---
concept_id: rust/complex/services/db/default_1
language: rust
okf_version: '0.2'
resource: rust/complex/services/db.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: default
type: Function
---

# default

## Signature

```rust
fn default() -> Self
```

## Source
Lines 65–67 in `rust/complex/services/db.rs`

```rs
    fn default() -> Self {
        Self::new()
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/rust/complex/services/db.md) |
