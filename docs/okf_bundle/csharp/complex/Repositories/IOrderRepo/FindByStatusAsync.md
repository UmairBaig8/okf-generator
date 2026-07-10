---
concept_id: csharp/complex/Repositories/IOrderRepo/FindByStatusAsync
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
title: FindByStatusAsync
type: Function
---

# FindByStatusAsync

## Signature

```csharp
FindByStatusAsync()
```

## Visibility

- `public`
- `async`

## Source
Lines 69–73 in `csharp/complex/Repositories/IOrderRepo.cs`

```cs
    public async Task<IEnumerable<Order>> FindByStatusAsync(OrderStatus status)
    {
        await Task.CompletedTask;
        return _store.Values.Where(o => o.Status == status);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [IOrderRepo](/csharp/complex/Repositories/IOrderRepo.md) |
