---
concept_id: java/complex/repository/OrderRepo/findByCustomerId
description: Finds all orders belonging to a specific customer.
language: java
okf_version: '0.2'
resource: java/complex/repository/OrderRepo.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-16T07:24:59Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [OrderRepo](/java/complex/repository/OrderRepo.md) |
| calls | [equals](/java/complex/model/Order/equals.md) |
| calls | [getCustomerId](/java/complex/model/Order/getCustomerId.md) |
