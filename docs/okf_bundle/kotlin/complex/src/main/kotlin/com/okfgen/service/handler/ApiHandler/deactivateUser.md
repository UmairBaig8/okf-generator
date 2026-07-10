---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler/deactivateUser
description: Deactivates a user account.
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: deactivateUser
type: Function
---

# deactivateUser

Deactivates a user account.

## Signature

```kotlin
fun deactivateUser(id: String)
```

## Docstring

Deactivates a user account.

## Source
Lines 40–45 in `kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.kt`

```kt
    fun deactivateUser(id: String): User? {
        val user = repo.findById(id) ?: return null
        val updated = user.deactivate()
        repo.save(updated)
        return updated
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | ApiHandler *(unresolved)* |
