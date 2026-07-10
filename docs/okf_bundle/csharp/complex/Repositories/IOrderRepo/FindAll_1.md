---
concept_id: csharp/complex/Repositories/IOrderRepo/FindAll_1
language: csharp
okf_version: '0.2'
resource: csharp/complex/Repositories/IOrderRepo.cs
tags:
- lang:csharp
- type:Function
- module:csharp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: FindAll
type: Function
---

# FindAll

## Signature

```csharp
FindAll()
```

## Visibility

- `public`

## Source
Lines 37–40 in `csharp/complex/Repositories/IOrderRepo.cs`

```cs
    public IReadOnlyList<Order> FindAll()
    {
        return _store.Values.ToList().AsReadOnly();
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [IOrderRepo](/csharp/complex/Repositories/IOrderRepo.md) |
