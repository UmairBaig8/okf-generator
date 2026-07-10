---
concept_id: rust/easy/math/is_prime
description: Check whether a number is prime using trial division.
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
timestamp: '2026-07-10T15:03:07Z'
title: is_prime
type: Function
---

# is_prime

Check whether a number is prime using trial division.

## Signature

```rust
pub fn is_prime(n: u64) -> bool
```

## Visibility

- `pub`

## Docstring

Check whether a number is prime using trial division.

## Source
Lines 22–37 in `rust/easy/math.rs`

```rs
pub fn is_prime(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    if n % 2 == 0 {
        return n == 2;
    }
    let mut i = 3;
    while i * i <= n {
        if n % i == 0 {
            return false;
        }
        i += 2;
    }
    true
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/rust/easy/math.md) |
