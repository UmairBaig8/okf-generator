---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/save_1
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: save
type: Function
---

# save

## Signature

```kotlin
fun save(user: User): User
```

## Source
Lines 23–26 in `kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt`

```kt
    override fun save(user: User): User {
        store[user.id] = user
        return user
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserRepository *(unresolved)* |
