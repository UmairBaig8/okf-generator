---
concept_id: rust/complex/services/db/test_insert_and_get_user
description: '[test]'
language: rust
okf_version: '0.2'
resource: rust/complex/services/db.rs
tags:
- lang:rust
- type:Function
- module:rust
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: test_insert_and_get_user
type: Function
---

# test_insert_and_get_user

[test]

## Signature

```rust
fn test_insert_and_get_user()
```

## Decorators

- `test`

## Docstring

[test]

## Source
Lines 75–82 in `rust/complex/services/db.rs`

```rs
    fn test_insert_and_get_user() {
        let mut repo = UserRepository::new();
        let user = User::new("alice@test.com", Some("Alice"));
        let id = repo.insert(user);
        let fetched = repo.get(&id);
        assert!(fetched.is_some());
        assert_eq!(fetched.unwrap().email, "alice@test.com");
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/rust/complex/services/db.md) |
