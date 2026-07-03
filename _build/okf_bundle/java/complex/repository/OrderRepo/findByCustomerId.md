---
description: Finds all orders belonging to a specific customer.
resource: java/complex/repository/OrderRepo.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:49Z'
title: findByCustomerId
type: Function
---

# findByCustomerId

Finds all orders belonging to a specific customer.

## Signature

```java
List<Order> findByCustomerId(String customerId)
```

## Visibility

- `public`

## Docstring

Finds all orders belonging to a specific customer.
@param customerId the customer identifier
@return list of orders for that customer

## Parameters

| Name | Type | Default |
|------|------|---------|
| `customerId` | `—` | `—` |

## Returns
`list of orders for that customer`

## Source
Lines 61–66 in `java/complex/repository/OrderRepo.java`

## Related

- [OrderRepo](/java/complex/repository/OrderRepo.md)

## Calls

- [equals](/java/complex/model/Order/equals.md)
- [getCustomerId](/java/complex/model/Order/getCustomerId.md)
