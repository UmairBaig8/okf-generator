---
concept_id: swift/complex/Sources/Service/Models/User/User
description: Represents a user in the system.
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Models/User.swift
tags:
- lang:swift
- type:Class
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: User
type: Class
---

# User

Represents a user in the system.

## Signature

```swift
struct User
```

## Inheritance

- `Identifiable`
- `Comparable`

## Docstring

Represents a user in the system.

## Methods

- `init`
- `deactivate`

## Source
Lines 4–27 in `swift/complex/Sources/Service/Models/User.swift`

```swift
public struct User: Identifiable, Comparable {
    public let id: String
    public var email: String
    public var displayName: String?
    public var isActive: Bool
    public let createdAt: Date

    public init(id: String, email: String, displayName: String? = nil) {
        self.id = id
        self.email = email
        self.displayName = displayName
        self.isActive = true
        self.createdAt = Date()
    }

    /// Deactivates the user account.
    public mutating func deactivate() {
        isActive = false
    }

    public static func < (lhs: User, rhs: User) -> Bool {
        lhs.createdAt < rhs.createdAt
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/swift/complex/Sources/Service/Models/User.md) |
