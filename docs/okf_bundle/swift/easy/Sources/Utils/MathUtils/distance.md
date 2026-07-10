---
concept_id: swift/easy/Sources/Utils/MathUtils/distance
description: Computes Euclidean distance to another point.
language: swift
okf_version: '0.2'
resource: swift/easy/Sources/Utils/MathUtils.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: distance
type: Function
---

# distance

Computes Euclidean distance to another point.

## Signature

```swift
func distance(to other: Point)
```

## Docstring

Computes Euclidean distance to another point.

## Source
Lines 31–35 in `swift/easy/Sources/Utils/MathUtils.swift`

```swift
    public func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return sqrt(dx * dx + dy * dy)
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | Point *(unresolved)* |
