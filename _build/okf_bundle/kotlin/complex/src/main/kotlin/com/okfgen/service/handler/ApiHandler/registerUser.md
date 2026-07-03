---
description: Registers a new user.
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-03T15:55:04Z'
title: registerUser
type: Function
---

# registerUser

Registers a new user.

## Signature

```kotlin
fun registerUser(email: String, displayName: String?): User
```

## Docstring

Registers a new user.
@throws IllegalArgumentException if the email is already taken.

## Source
Lines 15–23 in `kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.kt`

## Related

- ApiHandler *(unresolved)*
