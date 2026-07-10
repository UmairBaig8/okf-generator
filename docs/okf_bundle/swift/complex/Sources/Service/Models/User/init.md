---
concept_id: swift/complex/Sources/Service/Models/User/init
language: swift
okf_version: '0.2'
resource: swift/complex/Sources/Service/Models/User.swift
tags:
- lang:swift
- type:Function
- module:swift
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:12Z'
title: init
type: Function
---

# init

## Signature

```swift
init(id: String)
```

## Source
Lines 11–17 in `swift/complex/Sources/Service/Models/User.swift`

```swift
    public init(id: String, email: String, displayName: String? = nil) {
        self.id = id
        self.email = email
        self.displayName = displayName
        self.isActive = true
        self.createdAt = Date()
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | User *(unresolved)* |
