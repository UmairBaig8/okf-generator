---
concept_id: java/easy/model/User/setActive
language: java
okf_version: '0.2'
resource: java/easy/model/User.java
tags:
- lang:java
- type:Function
- module:java
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: setActive
type: Function
---

# setActive

## Signature

```java
void setActive(boolean active)
```

## Visibility

- `public`

## Source
Lines 66–68 in `java/easy/model/User.java`

```java
    public void setActive(boolean active) {
        this.active = active;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/java/easy/model/User.md) |
