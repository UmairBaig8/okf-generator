---
concept_id: rust/complex/services/db/default
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
timestamp: '2026-07-10T14:55:11Z'
title: default
type: Function
---

# default

## Signature

```rust
impl UserRepository { fn default() -> Self }
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
