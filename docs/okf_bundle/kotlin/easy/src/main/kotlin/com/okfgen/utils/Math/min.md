---
concept_id: kotlin/easy/src/main/kotlin/com/okfgen/utils/Math/min
description: Returns the smaller of two integers.
language: kotlin
okf_version: '0.2'
resource: kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: min
type: Function
---

# min

Returns the smaller of two integers.

## Signature

```kotlin
fun min(a: Int, b: Int): Int
```

## Docstring

Returns the smaller of two integers.

## Source
Lines 6–6 in `kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.kt`

```kt
fun min(a: Int, b: Int): Int = if (a < b) a else b
```

## Relationships

| Type | Target |
|------|--------|
| related | [Math](/kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.md) |
