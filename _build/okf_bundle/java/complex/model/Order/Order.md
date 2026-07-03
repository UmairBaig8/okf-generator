---
description: Represents a customer order in the payment processing system.
resource: java/complex/model/Order.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:42Z'
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

## Related

- [Order](/java/complex/model/Order.md)

## Calls

- [compareTo](/java/complex/model/Order/compareTo.md)
- [equals](/java/complex/model/Order/equals.md)
