---
concept_id: csharp/complex/Repositories/IOrderRepo/Save_1
language: csharp
okf_version: '0.2'
resource: csharp/complex/Repositories/IOrderRepo.cs
tags:
- lang:csharp
- type:Function
- module:csharp
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: Save
type: Function
---

# Save

## Signature

```csharp
Save()
```

## Visibility

- `public`

## Source
Lines 25–29 in `csharp/complex/Repositories/IOrderRepo.cs`

```cs
    public Order Save(Order order)
    {
        _store[order.Id] = order;
        return order;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [IOrderRepo](/csharp/complex/Repositories/IOrderRepo.md) |
