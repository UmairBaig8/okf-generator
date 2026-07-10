---
concept_id: swift/complex/Sources/Service/Repositories/UserRepository/listPaginated
description: Returns users sorted by creation date with pagination.
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Repositories/UserRepository.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: listPaginated
type: Function
---

# listPaginated

Returns users sorted by creation date with pagination.

## Signature

```swift
func listPaginated(page: Int)
```

## Docstring

Returns users sorted by creation date with pagination.

## Source
Lines 49–55 in `swift/complex/Sources/Service/Repositories/UserRepository.swift`

```swift
    public func listPaginated(page: Int, pageSize: Int) -> Paginated<User> {
        let all = store.values.sorted()
        let total = all.count
        let start = max(0, (page - 1) * pageSize)
        let items = Array(all.dropFirst(start).prefix(pageSize))
        return Paginated(items: items, total: total, page: page, pageSize: pageSize)
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserRepository *(unresolved)* |
