---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler/listActiveUsers
description: Lists all active users.
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: listActiveUsers
type: Function
---

# listActiveUsers

Lists all active users.

## Signature

```kotlin
fun listActiveUsers(): List<User>
```

## Docstring

Lists all active users.

## Source
Lines 34–35 in `kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.kt`

```kt
    fun listActiveUsers(): List<User> =
        repo.findBy { it.isActive }
```

## Relationships

| Type | Target |
|------|--------|
| related | ApiHandler *(unresolved)* |
| calls | [findBy](/kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/findBy.md) |
