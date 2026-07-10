---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/model/User/compareTo
language: kotlin
okf_version: '0.2'
resource: kotlin/complex/src/main/kotlin/com/okfgen/service/model/User.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: compareTo
type: Function
---

# compareTo

## Signature

```kotlin
fun compareTo(other: User): Int
```

## Source
Lines 21–22 in `kotlin/complex/src/main/kotlin/com/okfgen/service/model/User.kt`

```kt
    override fun compareTo(other: User): Int =
        this.createdAt.compareTo(other.createdAt)
```

## Relationships

| Type | Target |
|------|--------|
| related | User *(unresolved)* |
| called_by | [User](/kotlin/complex/src/main/kotlin/com/okfgen/service/model/User/User.md) |
