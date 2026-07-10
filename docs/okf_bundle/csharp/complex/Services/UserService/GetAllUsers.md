---
concept_id: csharp/complex/Services/UserService/GetAllUsers
language: csharp
okf_version: '0.2'
resource: csharp/complex/Services/UserService.cs
tags:
- lang:csharp
- type:Function
- module:csharp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: GetAllUsers
type: Function
---

# GetAllUsers

## Signature

```csharp
GetAllUsers()
```

## Visibility

- `public`

## Source
Lines 52–52 in `csharp/complex/Services/UserService.cs`

```cs
    public IReadOnlyList<User> GetAllUsers() => _users.AsReadOnly();
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserService](/csharp/complex/Services/UserService.md) |
