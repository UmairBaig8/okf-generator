---
concept_id: rust/easy/math/test_gcd
description: '[test]'
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
timestamp: '2026-07-07T06:58:42Z'
title: test_gcd
type: Function
---

# test_gcd

[test]

## Signature

```rust
fn test_gcd()
```

## Decorators

- `test`

## Docstring

[test]

## Source
Lines 55–58 in `rust/easy/math.rs`

```rs
    fn test_gcd() {
        assert_eq!(gcd(12, 8), 4);
        assert_eq!(gcd(17, 5), 1);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/rust/easy/math.md) |
