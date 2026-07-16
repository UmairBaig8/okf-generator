---
concept_id: java/complex/service/PaymentService/refund
description: Issues a full refund for the given transaction.
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
timestamp: '2026-07-16T08:14:30Z'
title: refund
type: Function
---

# refund

Issues a full refund for the given transaction.

## Signature

```java
boolean refund(String transactionId)
```

## Decorators

- `@Deprecated`

## Visibility

- `public`

## Docstring

Issues a full refund for the given transaction.
@param transactionId the original charge transaction ID
@return true if the refund was accepted
@deprecated Use {@link #refund(String, BigDecimal)} for partial refunds.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `transactionId` | `—` | `—` |

## Returns
`true if the refund was accepted`

## Source
Lines 48–51 in `java/complex/service/PaymentService.java`

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/java/complex/service/PaymentService.md) |
