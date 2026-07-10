---
concept_id: swift/complex/Sources/Service/Repositories/UserRepository/deleteById
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
timestamp: '2026-07-07T06:58:42Z'
title: deleteById
type: Function
---

# deleteById

## Signature

```swift
func deleteById(_ id: String)
```

## Source
Lines 40–42 in `swift/complex/Sources/Service/Repositories/UserRepository.swift`

```swift
    public func deleteById(_ id: String) -> Bool {
        store.removeValue(forKey: id) != nil
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserRepository *(unresolved)* |
