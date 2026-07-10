---
concept_id: rust/complex/services/db/Repository
description: Generic repository trait for entities that can be serialized.
language: rust
okf_version: '0.2'
resource: rust/complex/services/db.rs
tags:
- lang:rust
- type:Class
- module:rust
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Repository
type: Class
---

# Repository

Generic repository trait for entities that can be serialized.

## Signature

```rust
pub trait Repository
```

## Type Parameters

- `T: Serialize`

## Visibility

- `pub`

## Docstring

Generic repository trait for entities that can be serialized.

## Source
Lines 7–16 in `rust/complex/services/db.rs`

```rs
pub trait Repository<T: Serialize> {
    /// Insert a new entity into the repository.
    fn insert(&mut self, entity: T) -> String;
    /// Retrieve an entity by its ID.
    fn get(&self, id: &str) -> Option<&T>;
    /// Delete an entity by its ID.
    fn delete(&mut self, id: &str) -> bool;
    /// Return the number of entities stored.
    fn count(&self) -> usize;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/rust/complex/services/db.md) |
