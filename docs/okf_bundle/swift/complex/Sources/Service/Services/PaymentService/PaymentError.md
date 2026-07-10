---
concept_id: swift/complex/Sources/Service/Services/PaymentService/PaymentError
description: Errors that can occur during payment processing.
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Services/PaymentService.swift
tags:
- lang:swift
- type:Class
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:12Z'
title: PaymentError
type: Class
---

# PaymentError

Errors that can occur during payment processing.

## Signature

```swift
enum PaymentError
```

## Inheritance

- `Error`

## Docstring

Errors that can occur during payment processing.

## Source
Lines 4–8 in `swift/complex/Sources/Service/Services/PaymentService.swift`

```swift
public enum PaymentError: Error {
    case declined(reason: String)
    case invalidAmount
    case networkFailure
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/swift/complex/Sources/Service/Services/PaymentService.md) |
