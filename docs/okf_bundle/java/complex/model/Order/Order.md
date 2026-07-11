---
concept_id: java/complex/model/Order/Order
description: Represents a customer order in the payment processing system.
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
timestamp: '2026-07-11T11:35:27Z'
title: Order
type: Class
---

# Order

Represents a customer order in the payment processing system.

## Signature

```java
public class Order
```

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `String` | `private final` |
| `customerId` | `String` | `private final` |
| `items` | `List<OrderItem>` | `private final` |
| `status` | `Status` | `private` |
| `createdAt` | `LocalDateTime` | `private final` |
| `updatedAt` | `LocalDateTime` | `private` |

## Docstring

Represents a customer order in the payment processing system.

## Methods

- `Order`
- `addItem`
- `getTotal`
- `confirm`
- `cancel`
- `getId`
- `getCustomerId`
- `getItems`
- `getStatus`
- `getCreatedAt`
- `getUpdatedAt`
- `compareTo`
- `equals`
- `hashCode`
- `OrderItem`
- `getSubtotal`
- `getProductId`
- `getQuantity`
- `getUnitPrice`

## Source
Lines 12–129 in `java/complex/model/Order.java`

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
| calls | [add](/scala/complex/Router/add.md) |
| calls | [compareTo](/java/complex/model/Order/compareTo.md) |
| calls | [equals](/java/complex/model/Order/equals.md) |
| calls | [multiply](/dart/complex/router/multiply.md) |
