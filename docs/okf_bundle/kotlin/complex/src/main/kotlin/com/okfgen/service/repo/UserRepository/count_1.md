---
concept_id: kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository/count_1
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
timestamp: '2026-07-07T06:58:41Z'
title: count
type: Function
---

# count

## Signature

```kotlin
fun count(): Int
```

## Source
Lines 34–34 in `kotlin/complex/src/main/kotlin/com/okfgen/service/repo/UserRepository.kt`

```kt
    override fun count(): Int = store.size
```

## Relationships

| Type | Target |
|------|--------|
| related | UserRepository *(unresolved)* |
