---
concept_id: rust/easy/lib/Point
description: A simple struct representing a 2D coordinate.
language: rust
okf_version: '0.2'
resource: rust/easy/lib.rs
tags:
- lang:rust
- type:Class
- module:rust
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: Point
type: Class
---

# Point

A simple struct representing a 2D coordinate.

## Signature

```rust
pub struct Point
```

## Decorators

- `derive(Debug, Clone, Copy, PartialEq)`

## Visibility

- `pub`

## Docstring

A simple struct representing a 2D coordinate.
[derive(Debug, Clone, Copy, PartialEq)]

## Methods

- `x`
- `y`

## Source
Lines 38–41 in `rust/easy/lib.rs`

```rs
pub struct Point {
    pub x: f64,
    pub y: f64,
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [lib](/rust/easy/lib.md) |
