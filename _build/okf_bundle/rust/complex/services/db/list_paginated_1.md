---
description: List all users with pagination.
resource: rust/complex/services/db.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:44:03Z'
title: list_paginated
type: Function
---

# list_paginated

List all users with pagination.

## Signature

```rust
pub fn list_paginated(&self, page: u64, page_size: u64) -> Paginated<&User>
```

## Visibility

- `pub`

## Docstring

List all users with pagination.

## Source
Lines 32–41 in `rust/complex/services/db.rs`

## Related

- [db](/rust/complex/services/db.md)
