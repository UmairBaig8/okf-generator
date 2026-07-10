---
concept_id: java/complex/model/Order/getItems
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
timestamp: '2026-07-10T14:55:11Z'
title: getItems
type: Function
---

# getItems

## Signature

```java
List<OrderItem> getItems()
```

## Visibility

- `public`

## Source
Lines 85–85 in `java/complex/model/Order.java`

```java
    public List<OrderItem> getItems() { return new ArrayList<>(items); }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
