---
concept_id: java/complex/model/Order/compareTo
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
title: compareTo
type: Function
---

# compareTo

## Signature

```java
int compareTo(Order other)
```

## Decorators

- `@Override`

## Visibility

- `public`

## Source
Lines 90–93 in `java/complex/model/Order.java`

```java
    @Override
    public int compareTo(Order other) {
        return this.createdAt.compareTo(other.createdAt);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
| called_by | [Order](/java/complex/model/Order/Order.md) |
