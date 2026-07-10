---
concept_id: java/easy/model/User/User
description: Represents a user entity in the system.
language: java
okf_version: '0.2'
resource: java/easy/model/User.java
tags:
- lang:java
- type:Class
- module:java
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:37:52Z'
title: User
type: Class
---

# User

Represents a user entity in the system.

## Signature

```java
public class User
```

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `String` | `private final` |
| `email` | `String` | `private` |
| `displayName` | `String` | `private` |
| `active` | `boolean` | `private` |
| `createdAt` | `LocalDateTime` | `private final` |

## Docstring

Represents a user entity in the system.

## Methods

- `User`
- `User`
- `getId`
- `getEmail`
- `setEmail`
- `getDisplayName`
- `setDisplayName`
- `isActive`
- `setActive`
- `getCreatedAt`
- `equals`
- `hashCode`
- `toString`

## Source
Lines 9–90 in `java/easy/model/User.java`

## Relationships

| Type | Target |
|------|--------|
| related | [User](/java/easy/model/User.md) |
| calls | [equals](/java/easy/model/User/equals.md) |
