---
concept_id: java/complex/model/Order/OrderItem
description: Immutable value object representing a single line item.
language: java
okf_version: '0.2'
resource: java/complex/model/Order.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: OrderItem
type: Class
---

# OrderItem

Immutable value object representing a single line item.

## Signature

```java
public static class OrderItem
```

## Visibility

- `public`
- `static`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `productId` | `String` | `private final` |
| `quantity` | `int` | `private final` |
| `unitPrice` | `BigDecimal` | `private final` |

## Docstring

Immutable value object representing a single line item.

## Methods

- `OrderItem`
- `getSubtotal`
- `getProductId`
- `getQuantity`
- `getUnitPrice`

## Source
Lines 110–128 in `java/complex/model/Order.java`

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
| calls | [multiply](/dart/complex/router/multiply.md) |
