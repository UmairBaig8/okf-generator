---
concept_id: java/complex/repository/OrderRepo/save_1
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
timestamp: '2026-07-10T17:15:25Z'
title: save
type: Function
---

# save

## Signature

```java
Order save(Order order)
```

## Decorators

- `@Override`

## Visibility

- `public`

## Source
Lines 28–33 in `java/complex/repository/OrderRepo.java`

```java
    @Override
    public Order save(Order order) {
        Objects.requireNonNull(order, "Order must not be null");
        store.put(order.getId(), order);
        return order;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [OrderRepo](/java/complex/repository/OrderRepo.md) |
