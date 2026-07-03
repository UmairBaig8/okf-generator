---
description: Issues a refund for a transaction.
resource: swift/complex/Sources/Service/Services/PaymentService.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-03T15:54:51Z'
title: refund
type: Function
---

# refund

Issues a refund for a transaction.

## Signature

```swift
func refund(transactionId: String)
```

## Docstring

Issues a refund for a transaction.
- Parameter transactionId: The original charge transaction ID.
- Returns: `true` if the refund was accepted.

## Source
Lines 36–39 in `swift/complex/Sources/Service/Services/PaymentService.swift`

## Related

- PaymentService *(unresolved)*
