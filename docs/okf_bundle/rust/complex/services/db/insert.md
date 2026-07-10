---
concept_id: rust/complex/services/db/insert
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
title: insert
type: Function
---

# insert

## Signature

```rust
impl UserRepository { fn insert(&mut self, user: User) -> String }
```

## Source
Lines 45–49 in `rust/complex/services/db.rs`

```rs
    fn insert(&mut self, user: User) -> String {
        let id = user.id.clone();
        self.users.insert(id.clone(), user);
        id
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/rust/complex/services/db.md) |
