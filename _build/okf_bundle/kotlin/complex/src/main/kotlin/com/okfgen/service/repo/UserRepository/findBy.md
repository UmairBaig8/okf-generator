---
description: Finds users by a predicate.
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-03T15:55:02Z'
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

## Related

- UserRepository *(unresolved)*

## Called By

- [ApiHandler](/kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler/ApiHandler.md)
- [listActiveUsers](/kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler/listActiveUsers.md)
