---
description: Generic repository interface for entities with string IDs.
resource: java/complex/repository/OrderRepo.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:49Z'
title: Repository
type: Class
---

# Repository

Generic repository interface for entities with string IDs.

## Signature

```java
public interface Repository
```

## Type Parameters

- `T extends Comparable<T`

## Visibility

- `public`

## Docstring

Generic repository interface for entities with string IDs.
@param <T> entity type, must extend {@link Comparable}

## Methods

- `save`
- `findById`
- `findAll`
- `deleteById`
- `count`

## Source
Lines 13–19 in `java/complex/repository/OrderRepo.java`

## Related

- [OrderRepo](/java/complex/repository/OrderRepo.md)
