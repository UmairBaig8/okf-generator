---
concept_id: rust/complex/models/user/new
description: Create a new User with an auto-generated UUID.
language: rust
okf_version: '0.2'
resource: rust/complex/models/user.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T09:34:13Z'
title: new
type: Function
---

# new

Create a new User with an auto-generated UUID.

## Signature

```rust
impl User { pub fn new(email: &str, display_name: Option<&str>) -> Self }
```

## Visibility

- `pub`

## Docstring

Create a new User with an auto-generated UUID.

## Source
Lines 15–22 in `rust/complex/models/user.rs`

## Relationships

| Type | Target |
|------|--------|
| related | [user](/rust/complex/models/user.md) |
