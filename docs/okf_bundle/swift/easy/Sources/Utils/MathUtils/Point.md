---
concept_id: swift/easy/Sources/Utils/MathUtils/Point
description: Represents a 2D coordinate.
language: swift
okf_version: '0.2'
resource: swift/easy/Sources/Utils/MathUtils.swift
tags:
- lang:swift
- type:Class
- module:swift
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: Point
type: Class
---

# Point

Represents a 2D coordinate.

## Signature

```swift
struct Point
```

## Docstring

Represents a 2D coordinate.

## Methods

- `init`
- `distance`

## Source
Lines 21–36 in `swift/easy/Sources/Utils/MathUtils.swift`

```swift
public struct Point {
    public var x: Double
    public var y: Double

    public init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }

    /// Computes Euclidean distance to another point.
    public func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return sqrt(dx * dx + dy * dy)
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [MathUtils](/swift/easy/Sources/Utils/MathUtils.md) |
