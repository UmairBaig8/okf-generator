---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/Repository
description: Generic repository interface for CRUD operations.
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt
tags:
- lang:kotlin
- type:Interface
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:27:26Z'
title: Repository
type: Interface
---

# Repository

Generic repository interface for CRUD operations.

## Signature

```kotlin
interface Repository
```

## Type Parameters

- `T : Comparable<T>`

## Docstring

Generic repository interface for CRUD operations.

## Methods

- `save`
- `findById`
- `findAll`
- `deleteById`
- `count`

## Source
Lines 9–15 in `kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt`

## Relationships

| Type | Target |
|------|--------|
| related | [UserRepository](/kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.md) |
