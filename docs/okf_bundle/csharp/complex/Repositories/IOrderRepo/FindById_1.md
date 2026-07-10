---
concept_id: csharp/complex/Repositories/IOrderRepo/FindById_1
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
timestamp: '2026-07-10T14:57:28Z'
title: FindById
type: Function
---

# FindById

## Signature

```csharp
FindById()
```

## Visibility

- `public`

## Source
Lines 31–35 in `csharp/complex/Repositories/IOrderRepo.cs`

```cs
    public Order? FindById(string id)
    {
        _store.TryGetValue(id, out var order);
        return order;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [IOrderRepo](/csharp/complex/Repositories/IOrderRepo.md) |
