---
concept_id: csharp/complex/Repositories/IOrderRepo/OrderRepository
language: csharp
okf_version: '0.2'
resource: csharp/complex/Repositories/IOrderRepo.cs
tags:
- lang:csharp
- type:Class
- module:csharp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:08:02Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [IOrderRepo](/csharp/complex/Repositories/IOrderRepo.md) |
