---
concept_id: java/complex/repository/OrderRepo/Repository
description: Generic repository interface for entities with string IDs.
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
timestamp: '2026-07-10T18:32:37Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [OrderRepo](/java/complex/repository/OrderRepo.md) |
