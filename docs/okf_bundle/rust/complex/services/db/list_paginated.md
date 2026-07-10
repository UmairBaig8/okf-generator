---
concept_id: rust/complex/services/db/list_paginated
description: List all users with pagination.
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
timestamp: '2026-07-10T17:15:25Z'
title: list_paginated
type: Function
---

# list_paginated

List all users with pagination.

## Signature

```rust
impl UserRepository { pub fn list_paginated(&self, page: u64, page_size: u64) -> Paginated<&User> }
```

## Visibility

- `pub`

## Docstring

List all users with pagination.

## Source
Lines 32–41 in `rust/complex/services/db.rs`

```rs
    pub fn list_paginated(&self, page: u64, page_size: u64) -> Paginated<&User>
    where
        User: Serialize,
    {
        let all: Vec<&User> = self.users.values().collect();
        let total = all.len() as u64;
        let start = ((page.saturating_sub(1)) * page_size) as usize;
        let items: Vec<&User> = all.into_iter().skip(start).take(page_size as usize).collect();
        Paginated::new(items, total, page, page_size)
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/rust/complex/services/db.md) |
