---
description: Create a new paginated response.
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

## Related

- [user](/rust/complex/models/user.md)
