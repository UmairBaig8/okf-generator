---
concept_id: java/complex/repository/OrderRepo/OrderRepo
description: In-memory implementation of {@link Repository} for Order entities.
language: java
okf_version: '0.2'
resource: java/complex/repository/OrderRepo.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T20:08:44Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [OrderRepo](/java/complex/repository/OrderRepo.md) |
| calls | [equals](/java/complex/model/Order/equals.md) |
| calls | [getCustomerId](/java/complex/model/Order/getCustomerId.md) |
