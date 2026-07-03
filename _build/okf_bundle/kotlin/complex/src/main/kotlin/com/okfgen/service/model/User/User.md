---
description: Represents a user in the system.
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/model/User.kt
tags:
- lang:kotlin
- type:Class
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-03T15:54:58Z'
title: User
type: Class
---

# User

Represents a user in the system.

## Signature

```kotlin
class User
```

## Inheritance

- `Comparable<User>`

## Visibility

- `data`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `String` | `data` |
| `email` | `String` | `data` |
| `displayName` | `String?` | `data` |
| `isActive` | `Boolean` | `data` |
| `createdAt` | `Instant` | `data` |

## Docstring

Represents a user in the system.

## Methods

- `deactivate`
- `compareTo`

## Source
Lines 9–23 in `kotlin/complex/src/main/kotlin/com/okfgen/service/model/User.kt`

## Related

- [User](/kotlin/complex/src/main/kotlin/com/okfgen/service/model/User.md)

## Calls

- [toString](/java/easy/model/User/toString.md)
- [compareTo](/kotlin/complex/src/main/kotlin/com/okfgen/service/model/User/compareTo.md)
