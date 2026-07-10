---
concept_id: java/complex/model/Order/hashCode
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
title: hashCode
type: Function
---

# hashCode

## Signature

```java
int hashCode()
```

## Decorators

- `@Override`

## Visibility

- `public`

## Source
Lines 102–105 in `java/complex/model/Order.java`

```java
    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/java/complex/model/Order.md) |
