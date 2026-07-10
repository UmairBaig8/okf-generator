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
timestamp: '2026-07-10T17:15:25Z'
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

```cs
public class OrderRepository : IRepository<Order>
{
    private readonly Dictionary<string, Order> _store = new();

    public Order Save(Order order)
    {
        _store[order.Id] = order;
        return order;
    }

    public Order? FindById(string id)
    {
        _store.TryGetValue(id, out var order);
        return order;
    }

    public IReadOnlyList<Order> FindAll()
    {
        return _store.Values.ToList().AsReadOnly();
    }

    public bool Delete(string id)
    {
        return _store.Remove(id);
    }

    public long Count() => _store.Count;

    /// <summary>
    /// Finds all orders for a given customer, ordered by creation date.
    /// </summary>
    public IEnumerable<Order> FindByCustomer(string customerId)
    {
        return _store.Values
            .Where(o => o.CustomerId == customerId)
            .OrderBy(o => o.CreatedAt);
    }

    /// <summary>
    /// Finds all orders in a given status.
    /// </summary>
    [Obsolete("Use FindByStatusAsync instead for better performance.")]
    public IEnumerable<Order> FindByStatus(OrderStatus status)
    {
        return _store.Values.Where(o => o.Status == status);
    }

    /// <summary>Async version of FindByStatus.</summary>
    public async Task<IEnumerable<Order>> FindByStatusAsync(OrderStatus status)
    {
        await Task.CompletedTask;
        return _store.Values.Where(o => o.Status == status);
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [IOrderRepo](/csharp/complex/Repositories/IOrderRepo.md) |
