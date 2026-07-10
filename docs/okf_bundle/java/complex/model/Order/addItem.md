---
concept_id: java/complex/model/Order/addItem
description: Adds an item to this order.
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
title: addItem
type: Function
---

# addItem

Adds an item to this order.

## Signature

```java
void addItem(OrderItem item)
```

## Visibility

- `public`

## Docstring

Adds an item to this order.
@param item the item to add

## Parameters

| Name | Type | Default |
|------|------|---------|
| `item` | `—` | `—` |

## Source
Lines 46–49 in `java/complex/model/Order.java`

```java
    public void addItem(OrderItem item) {
        this.items.add(item);
        this.updatedAt = LocalDateTime.now();
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
| calls | [add](/scala/complex/Router/add.md) |
