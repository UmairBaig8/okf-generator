---
concept_id: rust/complex/services/db/get
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
title: get
type: Function
---

# get

## Signature

```rust
impl UserRepository { fn get(&self, id: &str) -> Option<&User> }
```

## Source
Lines 51–53 in `rust/complex/services/db.rs`

```rs
    fn get(&self, id: &str) -> Option<&User> {
        self.users.get(id)
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/rust/complex/services/db.md) |
