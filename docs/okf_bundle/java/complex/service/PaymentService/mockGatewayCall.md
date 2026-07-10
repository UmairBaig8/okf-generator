---
concept_id: java/complex/service/PaymentService/mockGatewayCall
description: Simulates a call to the external payment gateway.
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
timestamp: '2026-07-10T17:15:25Z'
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

```java
    private boolean mockGatewayCall(BigDecimal amount, String customerId) {
        return amount.compareTo(BigDecimal.valueOf(10000)) < 0;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [PaymentService](/java/complex/service/PaymentService.md) |
| called_by | [PaymentService](/java/complex/service/PaymentService/PaymentService.md) |
| called_by | [charge](/java/complex/service/PaymentService/charge.md) |
