---
concept_id: rust/complex/models/user/User
description: Represents a user in the system.
language: rust
okf_version: '0.2'
resource: rust/complex/models/user.rs
tags:
- lang:rust
- type:Class
- module:rust
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: User
type: Class
---

# User

Represents a user in the system.

## Signature

```rust
pub struct User
```

## Decorators

- `derive(Debug, Clone, Serialize, Deserialize)`

## Visibility

- `pub`

## Docstring

Represents a user in the system.
[derive(Debug, Clone, Serialize, Deserialize)]

## Methods

- `id`
- `email`
- `display_name`
- `active`

## Source
Lines 6–11 in `rust/complex/models/user.rs`

```rs
pub struct User {
    pub id: String,
    pub email: String,
    pub display_name: Option<String>,
    pub active: bool,
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/rust/complex/models/user.md) |
