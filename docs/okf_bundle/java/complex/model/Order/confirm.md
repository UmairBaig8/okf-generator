---
concept_id: java/complex/model/Order/confirm
description: Confirms the order, transitioning from PENDING to CONFIRMED.
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
timestamp: '2026-07-10T18:35:36Z'
title: confirm
type: Function
---

# confirm

Confirms the order, transitioning from PENDING to CONFIRMED.

## Signature

```java
void confirm()
```

## Visibility

- `public`

## Docstring

Confirms the order, transitioning from PENDING to CONFIRMED.
@throws IllegalStateException if the order is not in PENDING status

## Source
Lines 67–73 in `java/complex/model/Order.java`

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
