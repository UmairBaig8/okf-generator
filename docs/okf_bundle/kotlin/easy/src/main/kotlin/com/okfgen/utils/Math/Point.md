---
concept_id: kotlin/easy/src/main/kotlin/com/okfgen/utils/Math/Point
description: Represents a 2D coordinate.
language: kotlin
okf_version: '0.2'
resource: kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.kt
tags:
- lang:kotlin
- type:Class
- module:kotlin
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Point
type: Class
---

# Point

Represents a 2D coordinate.

## Signature

```kotlin
class Point
```

## Visibility

- `data`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `x` | `Double` | `data` |
| `y` | `Double` | `data` |

## Docstring

Represents a 2D coordinate.

## Methods

- `distanceTo`

## Source
Lines 27–36 in `kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.kt`

```kt
data class Point(val x: Double, val y: Double) {
    /**
     * Computes Euclidean distance to another point.
     */
    fun distanceTo(other: Point): Double {
        val dx = x - other.x
        val dy = y - other.y
        return kotlin.math.sqrt(dx * dx + dy * dy)
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Math](/kotlin/easy/src/main/kotlin/com/okfgen/utils/Math.md) |
