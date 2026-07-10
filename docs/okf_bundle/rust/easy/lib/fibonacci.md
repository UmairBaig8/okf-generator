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
timestamp: '2026-07-10T15:03:07Z'
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

```rs
pub fn fibonacci(n: i32) -> Option<u64> {
    if n < 0 {
        return None;
    }
    let n = n as usize;
    match n {
        0 => Some(0),
        1 => Some(1),
        _ => {
            let mut a = 0u64;
            let mut b = 1u64;
            for _ in 2..=n {
                let next = a.checked_add(b)?;
                a = b;
                b = next;
            }
            Some(b)
        }
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [lib](/rust/easy/lib.md) |
