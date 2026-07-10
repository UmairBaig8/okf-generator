---
concept_id: java/complex/model/Order/Status
description: Possible states of an order lifecycle.
language: java
okf_version: '0.2'
resource: java/complex/model/Order.java
tags:
- lang:java
- type:Class
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Status
type: Class
---

# Status

Possible states of an order lifecycle.

## Signature

```java
enum Status
```

## Visibility

- `public`

## Docstring

Possible states of an order lifecycle.

## Source
Lines 15–17 in `java/complex/model/Order.java`

```java
    public enum Status {
        PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
