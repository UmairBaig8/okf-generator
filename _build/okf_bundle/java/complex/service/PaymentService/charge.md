---
description: Processes payment for the given order.
resource: java/complex/service/PaymentService.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:46Z'
title: charge
type: Function
---

# charge

Processes payment for the given order.

## Signature

```java
String charge(Order order)
```

## Visibility

- `public`

## Docstring

Processes payment for the given order.
@param order the confirmed order to charge
@return a payment transaction ID
@throws IllegalArgumentException if the order is not confirmed
@throws PaymentDeclinedException if the gateway rejects the charge

## Parameters

| Name | Type | Default |
|------|------|---------|
| `order` | `—` | `—` |

## Returns
`a payment transaction ID`

## Source
Lines 26–39 in `java/complex/service/PaymentService.java`

## Related

- [PaymentService](/java/complex/service/PaymentService.md)

## Calls

- [getStatus](/java/complex/model/Order/getStatus.md)
- [getTotal](/java/complex/model/Order/getTotal.md)
- [toString](/java/easy/model/User/toString.md)
- [mockGatewayCall](/java/complex/service/PaymentService/mockGatewayCall.md)
- [getCustomerId](/java/complex/model/Order/getCustomerId.md)
