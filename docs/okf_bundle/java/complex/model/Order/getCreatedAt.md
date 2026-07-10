---
concept_id: java/complex/model/Order/getCreatedAt
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
title: getCreatedAt
type: Function
---

# getCreatedAt

## Signature

```java
LocalDateTime getCreatedAt()
```

## Visibility

- `public`

## Source
Lines 87–87 in `java/complex/model/Order.java`

```java
    public LocalDateTime getCreatedAt() { return createdAt; }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
