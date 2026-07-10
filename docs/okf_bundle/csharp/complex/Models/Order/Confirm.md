---
concept_id: csharp/complex/Models/Order/Confirm
language: csharp
okf_version: '0.2'
resource: csharp/complex/Models/Order.cs
tags:
- lang:csharp
- type:Function
- module:csharp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: Confirm
type: Function
---

# Confirm

## Signature

```csharp
Confirm()
```

## Visibility

- `public`

## Source
Lines 39–45 in `csharp/complex/Models/Order.cs`

```cs
    public void Confirm()
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException("Only pending orders can be confirmed.");
        Status = OrderStatus.Confirmed;
        UpdatedAt = DateTime.UtcNow;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Order](/csharp/complex/Models/Order.md) |
