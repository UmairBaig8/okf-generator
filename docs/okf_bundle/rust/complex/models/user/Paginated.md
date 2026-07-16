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
timestamp: '2026-07-16T07:24:59Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [user](/rust/complex/models/user.md) |
