---
concept_id: swift/complex/Sources/Service/Services/PaymentService/charge
description: Processes a payment for the given amount.
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Services/PaymentService.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-12T22:04:57Z'
title: charge
type: Function
---

# charge

Processes a payment for the given amount.

## Signature

```swift
func charge(amount: Decimal) throws
```

## Docstring

Processes a payment for the given amount.
- Parameter amount: The amount to charge.
- Returns: A transaction ID string.
- Throws: `PaymentError.declined` if the gateway rejects the charge.

## Source
Lines 22–31 in `swift/complex/Sources/Service/Services/PaymentService.swift`

## Relationships

| Type | Target |
|------|--------|
| related | PaymentService *(unresolved)* |
