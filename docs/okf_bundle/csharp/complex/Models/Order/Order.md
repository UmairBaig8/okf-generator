---
concept_id: csharp/complex/Models/Order/Order
language: csharp
okf_version: '0.2'
resource: csharp/complex/Models/Order.cs
tags:
- lang:csharp
- type:Class
- module:csharp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-16T08:11:36Z'
title: Order
type: Class
---

# Order

## Signature

```csharp
class Order
```

## Decorators

- `Serializable`

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `Id` | `string` | `public` |
| `CustomerId` | `string` | `public` |
| `Items` | `List<OrderItem>` | `public` |
| `Status` | `OrderStatus` | `public` |
| `CreatedAt` | `DateTime` | `public` |
| `UpdatedAt` | `DateTime` | `public` |

## Methods

- `GetTotal`
- `Confirm`

## Source
Lines 14–46 in `csharp/complex/Models/Order.cs`

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/csharp/complex/Models/Order.md) |
