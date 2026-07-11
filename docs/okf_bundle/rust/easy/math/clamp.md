---
concept_id: rust/easy/math/clamp
description: Clamp a value between a minimum and maximum.
language: rust
okf_version: '0.2'
resource: rust/easy/math.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T09:38:55Z'
title: clamp
type: Function
---

# clamp

Clamp a value between a minimum and maximum.

## Signature

```rust
pub fn clamp(value: T, min: T, max: T) -> T
```

## Type Parameters

- `T: PartialOrd`

## Visibility

- `pub`

## Docstring

Clamp a value between a minimum and maximum.

## Source
Lines 40–48 in `rust/easy/math.rs`

## Relationships

| Type | Target |
|------|--------|
| related | [math](/rust/easy/math.md) |
