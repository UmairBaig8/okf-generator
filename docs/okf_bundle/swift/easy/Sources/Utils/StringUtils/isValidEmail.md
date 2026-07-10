---
concept_id: swift/easy/Sources/Utils/StringUtils/isValidEmail
description: Validates email addresses using a basic pattern.
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
timestamp: '2026-07-10T17:15:25Z'
title: isValidEmail
type: Function
---

# isValidEmail

Validates email addresses using a basic pattern.

## Signature

```swift
func isValidEmail(_ email: String)
```

## Docstring

Validates email addresses using a basic pattern.

## Source
Lines 4–7 in `swift/easy/Sources/Utils/StringUtils.swift`

```swift
public func isValidEmail(_ email: String) -> Bool {
    let pattern = #"^[^\s@]+@[^\s@]+\.[^\s@]+$"#
    return email.range(of: pattern, options: .regularExpression) != nil
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [StringUtils](/swift/easy/Sources/Utils/StringUtils.md) |
