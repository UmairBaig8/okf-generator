---
description: Processes a payment for the given amount.
resource: swift/complex/Sources/Service/Services/PaymentService.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-03T15:54:51Z'
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

## Related

- PaymentService *(unresolved)*
