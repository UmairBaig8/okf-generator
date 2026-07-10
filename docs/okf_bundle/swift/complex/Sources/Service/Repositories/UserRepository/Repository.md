---
concept_id: swift/complex/Sources/Service/Repositories/UserRepository/Repository
description: Protocol defining CRUD operations for a generic entity type.
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Repositories/UserRepository.swift
tags:
- lang:swift
- type:Interface
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: Repository
type: Interface
---

# Repository

Protocol defining CRUD operations for a generic entity type.

## Signature

```swift
protocol Repository
```

## Type Parameters

- `T`

## Docstring

Protocol defining CRUD operations for a generic entity type.

## Source
Lines 4–11 in `swift/complex/Sources/Service/Repositories/UserRepository.swift`

```swift
public protocol Repository<T> {
    associatedtype T: Codable & Comparable
    func save(_ entity: T) -> T
    func findById(_ id: String) -> T?
    func findAll() -> [T]
    func deleteById(_ id: String) -> Bool
    func count() -> Int
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserRepository](/swift/complex/Sources/Service/Repositories/UserRepository.md) |
