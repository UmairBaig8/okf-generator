---
concept_id: java/complex/model/Order/getTotal
description: Calculates the total value of all items in this order.
language: java
okf_version: '0.2'
resource: java/complex/model/Order.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: getTotal
type: Function
---

# getTotal

Calculates the total value of all items in this order.

## Signature

```java
BigDecimal getTotal()
```

## Visibility

- `public`

## Docstring

Calculates the total value of all items in this order.
@return total as BigDecimal

## Returns
`total as BigDecimal`

## Source
Lines 56–60 in `java/complex/model/Order.java`

```java
    public BigDecimal getTotal() {
        return items.stream()
                .map(OrderItem::getSubtotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
| called_by | [PaymentService](/java/complex/service/PaymentService/PaymentService.md) |
| called_by | [charge](/java/complex/service/PaymentService/charge.md) |
