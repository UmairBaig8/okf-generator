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
timestamp: '2026-07-10T17:15:25Z'
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

```cs
[Serializable]
public class Order
{
    /// <summary>Unique order identifier.</summary>
    public string Id { get; init; }

    /// <summary>Customer who placed the order.</summary>
    public string CustomerId { get; init; }

    /// <summary>Line items in this order.</summary>
    public List<OrderItem> Items { get; set; } = new();

    /// <summary>Current order status.</summary>
    public OrderStatus Status { get; set; } = OrderStatus.Pending;

    /// <summary>Order creation timestamp.</summary>
    public DateTime CreatedAt { get; init; } = DateTime.UtcNow;

    /// <summary>Last modification timestamp.</summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>Calculates the total value of all items.</summary>
    public decimal GetTotal() => Items.Sum(i => i.UnitPrice * i.Quantity);

    /// <summary>Confirms the order.</summary>
    public void Confirm()
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException("Only pending orders can be confirmed.");
        Status = OrderStatus.Confirmed;
        UpdatedAt = DateTime.UtcNow;
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/csharp/complex/Models/Order.md) |
