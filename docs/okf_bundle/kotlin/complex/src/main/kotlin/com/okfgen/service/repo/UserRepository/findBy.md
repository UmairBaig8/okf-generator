---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/findBy
description: Finds users by a predicate.
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
timestamp: '2026-07-10T14:55:11Z'
title: findBy
type: Function
---

# findBy

Finds users by a predicate.

## Signature

```kotlin
fun findBy(predicate: (User) -> Boolean): List<User>
```

## Docstring

Finds users by a predicate.

## Source
Lines 50–51 in `kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt`

```kt
    inline fun findBy(predicate: (User) -> Boolean): List<User> =
        store.values.filter(predicate)
```

## Relationships

| Type | Target |
|------|--------|
| related | UserRepository *(unresolved)* |
| called_by | [ApiHandler](/kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler/ApiHandler.md) |
| called_by | [listActiveUsers](/kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler/listActiveUsers.md) |
