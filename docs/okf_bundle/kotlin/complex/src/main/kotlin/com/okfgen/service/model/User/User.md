---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/model/User/User
description: Represents a user in the system.
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/model/User.kt
tags:
- lang:kotlin
- type:Class
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
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

```kt
data class User(
    val id: String = UUID.randomUUID().toString(),
    val email: String,
    val displayName: String? = null,
    val isActive: Boolean = true,
    val createdAt: Instant = Instant.now()
) : Comparable<User> {
    /**
     * Deactivates the user account.
     */
    fun deactivate(): User = copy(isActive = false)

    override fun compareTo(other: User): Int =
        this.createdAt.compareTo(other.createdAt)
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/kotlin/complex/src/main/kotlin/com/okfgen/service/model/User.md) |
| calls | [toString](/java/easy/model/User/toString.md) |
| calls | [compareTo](/kotlin/complex/src/main/kotlin/com/okfgen/service/model/User/compareTo.md) |
