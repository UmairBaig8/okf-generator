---
concept_id: java/complex/model/Order/Order_1
description: Constructs a new Order.
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
timestamp: '2026-07-10T14:57:28Z'
title: Order
type: Function
---

# Order

Constructs a new Order.

## Signature

```java
Order(String id, String customerId)
```

## Visibility

- `public`

## Docstring

Constructs a new Order.
@param id         unique identifier
@param customerId owning customer

## Parameters

| Name | Type | Default |
|------|------|---------|
| `id` | `—` | `—` |

| `customerId` | `—` | `—` |

## Source
Lines 32–39 in `java/complex/model/Order.java`

```java
    public Order(String id, String customerId) {
        this.id = id;
        this.customerId = customerId;
        this.items = new ArrayList<>();
        this.status = Status.PENDING;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
