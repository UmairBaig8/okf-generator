---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/listPaginated
description: Returns users sorted by creation date with pagination.
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: listPaginated
type: Function
---

# listPaginated

Returns users sorted by creation date with pagination.

## Signature

```kotlin
fun listPaginated(page: Int, pageSize: Int): Paginated<User>
```

## Docstring

Returns users sorted by creation date with pagination.

## Source
Lines 39–45 in `kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt`

```kt
    fun listPaginated(page: Int, pageSize: Int): Paginated<User> {
        val all = store.values.sorted()
        val total = all.size
        val start = maxOf(0, (page - 1) * pageSize)
        val items = all.drop(start).take(pageSize)
        return Paginated(items = items, total = total, page = page, pageSize = pageSize)
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserRepository *(unresolved)* |
