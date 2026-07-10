---
concept_id: java/complex/repository/OrderRepo/deleteById_1
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
timestamp: '2026-07-10T15:03:07Z'
title: deleteById
type: Function
---

# deleteById

## Signature

```java
void deleteById(String id)
```

## Decorators

- `@Override`

## Visibility

- `public`

## Source
Lines 45–48 in `java/complex/repository/OrderRepo.java`

```java
    @Override
    public void deleteById(String id) {
        store.remove(id);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [OrderRepo](/java/complex/repository/OrderRepo.md) |
