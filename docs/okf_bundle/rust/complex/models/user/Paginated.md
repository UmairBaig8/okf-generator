---
concept_id: rust/complex/models/user/Paginated
description: Generic paginated wrapper for list responses.
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
timestamp: '2026-07-07T06:58:41Z'
title: Paginated
type: Class
---

# Paginated

Generic paginated wrapper for list responses.

## Signature

```rust
pub struct Paginated
```

## Type Parameters

- `T`

## Decorators

- `derive(Debug, Clone, Serialize)`

## Visibility

- `pub`

## Docstring

Generic paginated wrapper for list responses.
[derive(Debug, Clone, Serialize)]

## Methods

- `items`
- `total`
- `page`
- `page_size`

## Source
Lines 32–37 in `rust/complex/models/user.rs`

```rs
pub struct Paginated<T> {
    pub items: Vec<T>,
    pub total: u64,
    pub page: u64,
    pub page_size: u64,
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/rust/complex/models/user.md) |
