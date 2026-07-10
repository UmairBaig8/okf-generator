---
concept_id: csharp/easy/Models/User/User
language: csharp
okf_version: '0.2'
resource: csharp/easy/Models/User.cs
tags:
- lang:csharp
- type:Class
- module:csharp
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: User
type: Class
---

# User

## Signature

```csharp
class User
```

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `Id` | `string` | `public` |
| `Email` | `string` | `public` |
| `DisplayName` | `string?` | `public` |
| `IsActive` | `bool` | `public` |
| `CreatedAt` | `DateTime` | `public` |

## Methods

- `GetDisplayText`
- `Deactivate`

## Source
Lines 6–32 in `csharp/easy/Models/User.cs`

```cs
public class User
{
    /// <summary>Unique identifier.</summary>
    public string Id { get; init; }

    /// <summary>Email address.</summary>
    public string Email { get; set; }

    /// <summary>Display name.</summary>
    public string? DisplayName { get; set; }

    /// <summary>Whether the account is active.</summary>
    public bool IsActive { get; set; } = true;

    /// <summary>Timestamp of account creation.</summary>
    public DateTime CreatedAt { get; init; } = DateTime.UtcNow;

    /// <summary>
    /// Returns a display-friendly representation of the user.
    /// </summary>
    public string GetDisplayText() => DisplayName ?? Email;

    /// <summary>
    /// Deactivates the user account.
    /// </summary>
    public void Deactivate() => IsActive = false;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/csharp/easy/Models/User.md) |
