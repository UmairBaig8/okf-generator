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
timestamp: '2026-07-10T15:03:07Z'
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

```java
public class User {

    private final String id;
    private String email;
    private String displayName;
    private boolean active;
    private final LocalDateTime createdAt;

    /**
     * Constructs a new User with the given fields.
     *
     * @param id          unique identifier
     * @param email       email address
     * @param displayName optional display name
     */
    public User(String id, String email, String displayName) {
        this.id = id;
        this.email = email;
        this.displayName = displayName;
        this.active = true;
        this.createdAt = LocalDateTime.now();
    }

    /**
     * Constructs a minimal User with just an ID and email.
     *
     * @param id    unique identifier
     * @param email email address
     */
    public User(String id, String email) {
        this(id, email, null);
    }

    public String getId() {
        return id;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getDisplayName() {
        return displayName;
    }

    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User user)) return false;
        return Objects.equals(id, user.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "User{" + "id='" + id + '\'' + ", email='" + email + '\'' + '}';
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/java/easy/model/User.md) |
| calls | [equals](/java/easy/model/User/equals.md) |
