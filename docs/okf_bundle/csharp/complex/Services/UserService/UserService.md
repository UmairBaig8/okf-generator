---
concept_id: csharp/complex/Services/UserService/UserService
language: csharp
okf_version: '0.2'
resource: csharp/complex/Services/UserService.cs
tags:
- lang:csharp
- type:Class
- module:csharp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:11:01Z'
title: UserService
type: Class
---

# UserService

## Signature

```csharp
class UserService
```

## Visibility

- `public`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `_users` | `List<User>` | `private readonly` |
| `_nextId` | `int` | `private` |

## Methods

- `Register`
- `Login`
- `GetAllUsers`
- `HashPassword`
- `VerifyPassword`

## Source
Lines 6–65 in `csharp/complex/Services/UserService.cs`

## Relationships

| Type | Target |
|------|--------|
| related | [UserService](/csharp/complex/Services/UserService.md) |
