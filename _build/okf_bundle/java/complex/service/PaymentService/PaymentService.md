---
description: Service that processes payments for confirmed orders.
resource: java/complex/service/PaymentService.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:46Z'
title: PaymentService
type: Class
---

# PaymentService

Service that processes payments for confirmed orders.

## Signature

```java
public class PaymentService
```

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `gatewayApiKey` | `String` | `private final` |

## Docstring

Service that processes payments for confirmed orders.

## Methods

- `PaymentService`
- `charge`
- `refund`
- `refund`
- `mockGatewayCall`

## Source
Lines 10–74 in `java/complex/service/PaymentService.java`

## Related

- [PaymentService](/java/complex/service/PaymentService.md)

## Calls

- [getStatus](/java/complex/model/Order/getStatus.md)
- [getTotal](/java/complex/model/Order/getTotal.md)
- [toString](/java/easy/model/User/toString.md)
- [mockGatewayCall](/java/complex/service/PaymentService/mockGatewayCall.md)
- [getCustomerId](/java/complex/model/Order/getCustomerId.md)
