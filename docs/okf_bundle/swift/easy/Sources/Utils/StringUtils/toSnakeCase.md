---
concept_id: swift/easy/Sources/Utils/StringUtils/toSnakeCase
description: Converts a CamelCase string to snake_case.
language: swift
okf_version: '0.2'
resource: swift/easy/Sources/Utils/StringUtils.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:12Z'
title: toSnakeCase
type: Function
---

# toSnakeCase

Converts a CamelCase string to snake_case.

## Signature

```swift
func toSnakeCase(_ camel: String)
```

## Docstring

Converts a CamelCase string to snake_case.

## Source
Lines 18–31 in `swift/easy/Sources/Utils/StringUtils.swift`

```swift
public func toSnakeCase(_ camel: String) -> String {
    var result = ""
    for (i, char) in camel.enumerated() {
        if char.isUppercase {
            if i > 0 {
                result.append("_")
            }
            result.append(char.lowercased())
        } else {
            result.append(char)
        }
    }
    return result
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [StringUtils](/swift/easy/Sources/Utils/StringUtils.md) |
