---
concept_id: swift/easy/Sources/Utils/MathUtils/max
description: Returns the larger of two integers.
language: swift
okf_version: '0.2'
resource: swift/easy/Sources/Utils/MathUtils.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: max
type: Function
---

# max

Returns the larger of two integers.

## Signature

```swift
func max(_ a: Int)
```

## Docstring

Returns the larger of two integers.

## Source
Lines 9–11 in `swift/easy/Sources/Utils/MathUtils.swift`

```swift
public func max(_ a: Int, _ b: Int) -> Int {
    a > b ? a : b
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [MathUtils](/swift/easy/Sources/Utils/MathUtils.md) |
