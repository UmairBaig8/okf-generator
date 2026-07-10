---
concept_id: rust/complex/models/user/new_1
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
timestamp: '2026-07-10T14:55:11Z'
title: new
type: Function
---

# new

Create a new User with an auto-generated UUID.

## Signature

```rust
pub fn new(email: &str, display_name: Option<&str>) -> Self
```

## Visibility

- `pub`

## Docstring

Create a new User with an auto-generated UUID.

## Source
Lines 15–22 in `rust/complex/models/user.rs`

```rs
    pub fn new(email: &str, display_name: Option<&str>) -> Self {
        User {
            id: Uuid::new_v4().to_string(),
            email: email.to_string(),
            display_name: display_name.map(|s| s.to_string()),
            active: true,
        }
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/rust/complex/models/user.md) |
