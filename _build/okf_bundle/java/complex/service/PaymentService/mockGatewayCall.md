---
description: Simulates a call to the external payment gateway.
resource: java/complex/service/PaymentService.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:46Z'
title: mockGatewayCall
type: Function
---

# mockGatewayCall

Simulates a call to the external payment gateway.

## Signature

```java
boolean mockGatewayCall(BigDecimal amount, String customerId)
```

## Visibility

- `private`

## Docstring

Simulates a call to the external payment gateway.

## Source
Lines 71–73 in `java/complex/service/PaymentService.java`

## Related

- [PaymentService](/java/complex/service/PaymentService.md)

## Called By

- [PaymentService](/java/complex/service/PaymentService/PaymentService.md)
- [charge](/java/complex/service/PaymentService/charge.md)
