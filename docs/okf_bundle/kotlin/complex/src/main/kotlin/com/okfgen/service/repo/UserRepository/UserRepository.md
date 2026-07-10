---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/UserRepository
description: In-memory implementation of Repository for User entities.
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt
tags:
- lang:kotlin
- type:Class
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: UserRepository
type: Class
---

# UserRepository

In-memory implementation of Repository for User entities.

## Signature

```kotlin
class UserRepository
```

## Inheritance

- `Repository<User>`

## Docstring

In-memory implementation of Repository for User entities.

## Methods

- `save`
- `findById`
- `findAll`
- `deleteById`
- `count`
- `listPaginated`
- `findBy`

## Source
Lines 20–52 in `kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt`

```kt
class UserRepository : Repository<User> {
    private val store = mutableMapOf<String, User>()

    override fun save(user: User): User {
        store[user.id] = user
        return user
    }

    override fun findById(id: String): User? = store[id]

    override fun findAll(): List<User> = store.values.toList()

    override fun deleteById(id: String): Boolean = store.remove(id) != null

    override fun count(): Int = store.size

    /**
     * Returns users sorted by creation date with pagination.
     */
    fun listPaginated(page: Int, pageSize: Int): Paginated<User> {
        val all = store.values.sorted()
        val total = all.size
        val start = maxOf(0, (page - 1) * pageSize)
        val items = all.drop(start).take(pageSize)
        return Paginated(items = items, total = total, page = page, pageSize = pageSize)
    }

    /**
     * Finds users by a predicate.
     */
    inline fun findBy(predicate: (User) -> Boolean): List<User> =
        store.values.filter(predicate)
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserRepository](/kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.md) |
