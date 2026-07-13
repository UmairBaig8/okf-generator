---
concept_id: java/complex/service/PaymentService/charge
description: Processes payment for the given order.
language: java
okf_version: '0.2'
resource: java/complex/service/PaymentService.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-13T20:34:09Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/java/complex/service/PaymentService.md) |
| calls | [getStatus](/java/complex/model/Order/getStatus.md) |
| calls | [getTotal](/java/complex/model/Order/getTotal.md) |
| calls | [toString](/java/easy/model/User/toString.md) |
| calls | [mockGatewayCall](/java/complex/service/PaymentService/mockGatewayCall.md) |
| calls | [getCustomerId](/java/complex/model/Order/getCustomerId.md) |
