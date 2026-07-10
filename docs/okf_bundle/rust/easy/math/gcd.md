---
concept_id: rust/easy/math/gcd
description: Compute the greatest common divisor of two positive integers using Euclid's
  algorithm.
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
timestamp: '2026-07-10T17:15:25Z'
title: gcd
type: Function
---

# gcd

Compute the greatest common divisor of two positive integers using Euclid's algorithm.

## Signature

```rust
pub fn gcd(a: u64, b: u64) -> u64
```

## Visibility

- `pub`

## Docstring

Compute the greatest common divisor of two positive integers using Euclid's algorithm.

## Source
Lines 4–10 in `rust/easy/math.rs`

```rs
pub fn gcd(a: u64, b: u64) -> u64 {
    if b == 0 {
        a
    } else {
        gcd(b, a % b)
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/rust/easy/math.md) |
| called_by | [lcm](/rust/easy/math/lcm.md) |
