---
description: Create a new User with an auto-generated UUID.
resource: rust/complex/models/user.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:59Z'
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

## Related

- [user](/rust/complex/models/user.md)
