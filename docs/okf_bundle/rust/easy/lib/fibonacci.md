---
concept_id: rust/easy/lib/fibonacci
description: Computes the nth Fibonacci number iteratively.
language: rust
okf_version: '0.2'
resource: rust/easy/lib.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:52:39Z'
title: fibonacci
type: Function
---

# fibonacci

Computes the nth Fibonacci number iteratively.

## Signature

```rust
pub fn fibonacci(n: i32) -> Option<u64>
```

## Visibility

- `pub`

## Docstring

Computes the nth Fibonacci number iteratively.

Returns `None` if `n` is negative, otherwise `Some(u64)`.

## Source
Lines 7–26 in `rust/easy/lib.rs`

## Relationships

| Type | Target |
|------|--------|
| related | [lib](/rust/easy/lib.md) |
