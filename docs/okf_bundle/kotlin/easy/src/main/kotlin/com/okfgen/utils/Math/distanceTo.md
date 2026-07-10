---
concept_id: kotlin/easy/src/main/kotlin/com/okfgen/utils/Math/distanceTo
description: Computes Euclidean distance to another point.
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
timestamp: '2026-07-10T17:15:25Z'
title: distanceTo
type: Function
---

# distanceTo

Computes Euclidean distance to another point.

## Signature

```kotlin
fun distanceTo(other: Point): Double
```

## Docstring

Computes Euclidean distance to another point.

## Source
Lines 31–35 in `kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.kt`

```kt
    fun distanceTo(other: Point): Double {
        val dx = x - other.x
        val dy = y - other.y
        return kotlin.math.sqrt(dx * dx + dy * dy)
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | Point *(unresolved)* |
