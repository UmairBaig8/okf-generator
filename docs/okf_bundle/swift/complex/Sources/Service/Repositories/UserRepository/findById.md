---
concept_id: swift/complex/Sources/Service/Repositories/UserRepository/findById
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
timestamp: '2026-07-10T14:57:28Z'
title: findById
type: Function
---

# findById

## Signature

```swift
func findById(_ id: String)
```

## Source
Lines 32–34 in `swift/complex/Sources/Service/Repositories/UserRepository.swift`

```swift
    public func findById(_ id: String) -> User? {
        store[id]
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserRepository *(unresolved)* |
