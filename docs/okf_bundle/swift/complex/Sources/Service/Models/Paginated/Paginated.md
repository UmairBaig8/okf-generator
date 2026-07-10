---
concept_id: swift/complex/Sources/Service/Models/Paginated/Paginated
description: Generic paginated wrapper for list responses.
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Models/Paginated.swift
tags:
- lang:swift
- type:Class
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: Paginated
type: Class
---

# Paginated

Generic paginated wrapper for list responses.

## Signature

```swift
struct Paginated
```

## Type Parameters

- `T: Codable`

## Inheritance

- `Codable`

## Docstring

Generic paginated wrapper for list responses.

## Methods

- `init`

## Source
Lines 4–16 in `swift/complex/Sources/Service/Models/Paginated.swift`

```swift
public struct Paginated<T: Codable>: Codable {
    public let items: [T]
    public let total: Int
    public let page: Int
    public let pageSize: Int

    public init(items: [T], total: Int, page: Int, pageSize: Int) {
        self.items = items
        self.total = total
        self.page = page
        self.pageSize = pageSize
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Paginated](/swift/complex/Sources/Service/Models/Paginated.md) |
