---
concept_id: rust/easy/lib/distance_to
description: Compute the Euclidean distance to another point.
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
timestamp: '2026-07-10T14:55:11Z'
title: distance_to
type: Function
---

# distance_to

Compute the Euclidean distance to another point.

## Signature

```rust
impl Point { pub fn distance_to(&self, other: &Point) -> f64 }
```

## Visibility

- `pub`

## Docstring

Compute the Euclidean distance to another point.

## Source
Lines 50–54 in `rust/easy/lib.rs`

```rs
    pub fn distance_to(&self, other: &Point) -> f64 {
        let dx = self.x - other.x;
        let dy = self.y - other.y;
        (dx * dx + dy * dy).sqrt()
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [lib](/rust/easy/lib.md) |
