---
concept_id: kotlin/easy/src/main/kotlin/com/okfgen/utils/Math/clamp
description: Clamps a value between a minimum and maximum.
language: kotlin
okf_version: '0.2'
resource: kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.kt
tags:
- lang:kotlin
- type:Function
- module:kotlin
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: clamp
type: Function
---

# clamp

Clamps a value between a minimum and maximum.

## Signature

```kotlin
fun clamp(value: T, low: T, high: T): T
```

## Docstring

Clamps a value between a minimum and maximum.

## Source
Lines 16–22 in `kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.kt`

```kt
fun <T : Comparable<T>> clamp(value: T, low: T, high: T): T {
    return when {
        value < low -> low
        value > high -> high
        else -> value
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Math](/kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.md) |
