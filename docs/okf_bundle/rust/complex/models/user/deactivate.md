---
concept_id: rust/complex/models/user/deactivate
description: Deactivate this user account.
language: rust
okf_version: '0.2'
resource: rust/complex/models/user.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: deactivate
type: Function
---

# deactivate

Deactivate this user account.

## Signature

```rust
impl User { pub fn deactivate(&mut self) }
```

## Visibility

- `pub`

## Docstring

Deactivate this user account.

## Source
Lines 25–27 in `rust/complex/models/user.rs`

```rs
    pub fn deactivate(&mut self) {
        self.active = false;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/rust/complex/models/user.md) |
