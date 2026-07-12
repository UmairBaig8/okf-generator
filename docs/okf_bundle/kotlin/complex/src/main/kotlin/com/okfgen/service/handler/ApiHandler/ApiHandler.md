---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler/ApiHandler
description: Handles API requests for user operations.
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.kt
tags:
- lang:kotlin
- type:Class
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-12T09:19:36Z'
title: ApiHandler
type: Class
---

# ApiHandler

Handles API requests for user operations.

## Signature

```kotlin
class ApiHandler
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `repo` | `UserRepository` | `` |

## Docstring

Handles API requests for user operations.

## Methods

- `registerUser`
- `getUser`
- `listActiveUsers`
- `deactivateUser`

## Source
Lines 9–46 in `kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.kt`

## Relationships

| Type | Target |
|------|--------|
| related | [ApiHandler](/kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.md) |
| calls | [findBy](/kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/findBy.md) |
