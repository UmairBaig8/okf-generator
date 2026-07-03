---
resource: csharp/complex/Repositories/IOrderRepo.cs
tags:
- lang:csharp
- type:Class
- module:csharp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:44:54Z'
title: OrderRepository
type: Class
---

# OrderRepository

## Signature

```csharp
class OrderRepository
```

## Inheritance

- `IRepository<Order>`

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `_store` | `Dictionary<string, Order>` | `private readonly` |

## Methods

- `Save`
- `FindById`
- `FindAll`
- `Delete`
- `Count`
- `FindByCustomer`
- `FindByStatus`
- `FindByStatusAsync`

## Source
Lines 21–74 in `csharp/complex/Repositories/IOrderRepo.cs`

## Related

- [IOrderRepo](/csharp/complex/Repositories/IOrderRepo.md)
