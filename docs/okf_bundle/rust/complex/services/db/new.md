---
concept_id: rust/complex/services/db/new
description: Create a new empty UserRepository.
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
title: new
type: Function
---

# new

Create a new empty UserRepository.

## Signature

```rust
impl UserRepository { pub fn new() -> Self }
```

## Visibility

- `pub`

## Docstring

Create a new empty UserRepository.

## Source
Lines 25–29 in `rust/complex/services/db.rs`

```rs
    pub fn new() -> Self {
        UserRepository {
            users: HashMap::new(),
        }
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/rust/complex/services/db.md) |
