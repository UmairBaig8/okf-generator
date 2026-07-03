---
description: Issues a refund (full or partial) for the given transaction.
resource: java/complex/service/PaymentService.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:46Z'
title: refund
type: Function
---

# refund

Issues a refund (full or partial) for the given transaction.

## Signature

```java
boolean refund(String transactionId, BigDecimal amount)
```

## Decorators

- `@SuppressWarnings("unused")`

## Visibility

- `public`

## Docstring

Issues a refund (full or partial) for the given transaction.
@param transactionId the original charge transaction ID
@param amount        optional partial amount; null means full refund
@return true if the refund was accepted

## Parameters

| Name | Type | Default |
|------|------|---------|
| `transactionId` | `—` | `—` |
| `amount` | `—` | `—` |

## Returns
`true if the refund was accepted`

## Source
Lines 60–66 in `java/complex/service/PaymentService.java`

## Related

- [PaymentService](/java/complex/service/PaymentService.md)
