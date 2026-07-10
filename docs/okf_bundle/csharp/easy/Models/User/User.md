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
timestamp: '2026-07-10T18:42:48Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [User](/csharp/easy/Models/User.md) |
