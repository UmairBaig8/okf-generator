---
description: Confirms the order, transitioning from PENDING to CONFIRMED.
resource: java/complex/model/Order.java
tags:
- lang:java
- type:Function
- module:java
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:42Z'
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

## Related

- [Order](/java/complex/model/Order.md)
