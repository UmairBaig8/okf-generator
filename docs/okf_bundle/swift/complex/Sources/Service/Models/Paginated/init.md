---
concept_id: swift/complex/Sources/Service/Models/Paginated/init
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Models/Paginated.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: init
type: Function
---

# init

## Signature

```swift
init(items: [T])
```

## Source
Lines 10–15 in `swift/complex/Sources/Service/Models/Paginated.swift`

```swift
    public init(items: [T], total: Int, page: Int, pageSize: Int) {
        self.items = items
        self.total = total
        self.page = page
        self.pageSize = pageSize
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | Paginated *(unresolved)* |
