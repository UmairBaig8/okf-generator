---
concept_id: swift/easy/Sources/Utils/MathUtils/clamp
description: Clamps a value between a minimum and maximum.
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
title: clamp
type: Function
---

# clamp

Clamps a value between a minimum and maximum.

## Signature

```swift
func clamp(_ value: T)
```

## Docstring

Clamps a value between a minimum and maximum.

## Source
Lines 14–18 in `swift/easy/Sources/Utils/MathUtils.swift`

```swift
public func clamp<T: Comparable>(_ value: T, low: T, high: T) -> T {
    if value < low { return low }
    if value > high { return high }
    return value
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [MathUtils](/swift/easy/Sources/Utils/MathUtils.md) |
