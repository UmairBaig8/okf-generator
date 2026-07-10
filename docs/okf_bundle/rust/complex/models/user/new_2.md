---
concept_id: rust/complex/models/user/new_2
description: Create a new paginated response.
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
timestamp: '2026-07-10T17:42:36Z'
title: new
type: Function
---

# new

Create a new paginated response.

## Signature

```rust
impl Paginated<T> { pub fn new(items: Vec<T>, total: u64, page: u64, page_size: u64) -> Self }
```

## Type Parameters

- `T`

## Visibility

- `pub`

## Docstring

Create a new paginated response.

## Source
Lines 41–48 in `rust/complex/models/user.rs`

## Relationships

| Type | Target |
|------|--------|
| related | [user](/rust/complex/models/user.md) |
