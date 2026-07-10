---
concept_id: java/complex/model/Order/cancel
description: Cancels the order.
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
timestamp: '2026-07-10T17:15:25Z'
title: cancel
type: Function
---

# cancel

Cancels the order.

## Signature

```java
void cancel()
```

## Visibility

- `public`

## Docstring

Cancels the order.

## Source
Lines 78–81 in `java/complex/model/Order.java`

```java
    public void cancel() {
        this.status = Status.CANCELLED;
        this.updatedAt = LocalDateTime.now();
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
