---
concept_id: swift/complex/Sources/Service/Repositories/UserRepository/UserRepository
description: In-memory implementation of Repository for User entities.
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Repositories/UserRepository.swift
tags:
- lang:swift
- type:Class
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: UserRepository
type: Class
---

# UserRepository

In-memory implementation of Repository for User entities.

## Signature

```swift
class UserRepository
```

## Inheritance

- `Repository`

## Docstring

In-memory implementation of Repository for User entities.

## Methods

- `init`
- `save`
- `findById`
- `findAll`
- `deleteById`
- `count`
- `listPaginated`

## Source
Lines 21–56 in `swift/complex/Sources/Service/Repositories/UserRepository.swift`

```swift
public class UserRepository: Repository {
    public typealias T = User
    private var store: [String: User] = [:]

    public init() {}

    public func save(_ user: User) -> User {
        store[user.id] = user
        return user
    }

    public func findById(_ id: String) -> User? {
        store[id]
    }

    public func findAll() -> [User] {
        Array(store.values)
    }

    public func deleteById(_ id: String) -> Bool {
        store.removeValue(forKey: id) != nil
    }

    public func count() -> Int {
        store.count
    }

    /// Returns users sorted by creation date with pagination.
    public func listPaginated(page: Int, pageSize: Int) -> Paginated<User> {
        let all = store.values.sorted()
        let total = all.count
        let start = max(0, (page - 1) * pageSize)
        let items = Array(all.dropFirst(start).prefix(pageSize))
        return Paginated(items: items, total: total, page: page, pageSize: pageSize)
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserRepository](/swift/complex/Sources/Service/Repositories/UserRepository.md) |
