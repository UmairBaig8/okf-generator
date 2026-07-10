---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler/registerUser
description: Registers a new user.
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
timestamp: '2026-07-10T17:51:27Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | ApiHandler *(unresolved)* |
