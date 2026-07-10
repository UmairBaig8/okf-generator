---
concept_id: rust/complex/services/db/count
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
timestamp: '2026-07-10T15:03:07Z'
title: count
type: Function
---

# count

## Signature

```rust
impl UserRepository { fn count(&self) -> usize }
```

## Source
Lines 59–61 in `rust/complex/services/db.rs`

```rs
    fn count(&self) -> usize {
        self.users.len()
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/rust/complex/services/db.md) |
