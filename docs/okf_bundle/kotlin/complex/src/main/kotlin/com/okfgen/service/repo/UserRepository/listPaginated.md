---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/listPaginated
description: Returns users sorted by creation date with pagination.
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:59:43Z'
title: listPaginated
type: Function
---

# listPaginated

Returns users sorted by creation date with pagination.

## Signature

```kotlin
fun listPaginated(page: Int, pageSize: Int): Paginated<User>
```

## Docstring

Returns users sorted by creation date with pagination.

## Source
Lines 39–45 in `kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt`

## Relationships

| Type | Target |
|------|--------|
| related | UserRepository *(unresolved)* |
