---
concept_id: java/complex/service/PaymentService/PaymentService
description: Service that processes payments for confirmed orders.
language: java
okf_version: '0.2'
resource: java/complex/service/PaymentService.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-16T08:11:36Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/java/complex/service/PaymentService.md) |
| calls | [getStatus](/java/complex/model/Order/getStatus.md) |
| calls | [getTotal](/java/complex/model/Order/getTotal.md) |
| calls | [toString](/java/easy/model/User/toString.md) |
| calls | [mockGatewayCall](/java/complex/service/PaymentService/mockGatewayCall.md) |
| calls | [getCustomerId](/java/complex/model/Order/getCustomerId.md) |
