---
concept_id: java/easy/model/User/equals
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
title: equals
type: Function
---

# equals

## Signature

```java
boolean equals(Object o)
```

## Decorators

- `@Override`

## Visibility

- `public`

## Source
Lines 74–79 in `java/easy/model/User.java`

```java
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User user)) return false;
        return Objects.equals(id, user.id);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/java/easy/model/User.md) |
| called_by | [User](/java/easy/model/User/User.md) |
