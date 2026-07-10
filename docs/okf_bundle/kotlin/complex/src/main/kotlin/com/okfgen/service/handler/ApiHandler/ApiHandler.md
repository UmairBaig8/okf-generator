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
timestamp: '2026-07-10T17:15:25Z'
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

```kt
class ApiHandler(private val repo: UserRepository) {

    /**
     * Registers a new user.
     * @throws IllegalArgumentException if the email is already taken.
     */
    fun registerUser(email: String, displayName: String?): User {
        require(email.isNotBlank()) { "Email is required" }
        val existing = repo.findAll().firstOrNull { it.email == email }
        if (existing != null) {
            throw IllegalArgumentException("Email already registered")
        }
        val user = User(email = email, displayName = displayName)
        return repo.save(user)
    }

    /**
     * Retrieves a user by ID.
     * @return the user, or null if not found.
     */
    fun getUser(id: String): User? = repo.findById(id)

    /**
     * Lists all active users.
     */
    fun listActiveUsers(): List<User> =
        repo.findBy { it.isActive }

    /**
     * Deactivates a user account.
     */
    fun deactivateUser(id: String): User? {
        val user = repo.findById(id) ?: return null
        val updated = user.deactivate()
        repo.save(updated)
        return updated
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [ApiHandler](/kotlin/complex/src/main/kotlin/com/okfgen/service/handler/ApiHandler.md) |
| calls | [findBy](/kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/findBy.md) |
