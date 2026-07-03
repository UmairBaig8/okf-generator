---
description: In-memory implementation of {@link Repository} for Order entities.
resource: java/complex/repository/OrderRepo.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:49Z'
title: OrderRepo
type: Class
---

# OrderRepo

In-memory implementation of {@link Repository} for Order entities.

## Signature

```java
public class OrderRepo
```

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `store` | `Map<String, Order>` | `private final` |

## Docstring

In-memory implementation of {@link Repository} for Order entities.

## Methods

- `save`
- `findById`
- `findAll`
- `deleteById`
- `count`
- `findByCustomerId`

## Source
Lines 24–67 in `java/complex/repository/OrderRepo.java`

## Related

- [OrderRepo](/java/complex/repository/OrderRepo.md)

## Calls

- [getId](/java/complex/model/Order/getId.md)
- [equals](/java/complex/model/Order/equals.md)
- [getCustomerId](/java/complex/model/Order/getCustomerId.md)
