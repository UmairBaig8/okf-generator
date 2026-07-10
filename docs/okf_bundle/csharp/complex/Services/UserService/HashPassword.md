---
concept_id: csharp/complex/Services/UserService/HashPassword
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
title: HashPassword
type: Function
---

# HashPassword

## Signature

```csharp
HashPassword()
```

## Visibility

- `private`
- `static`

## Source
Lines 54–59 in `csharp/complex/Services/UserService.cs`

```cs
    private static string HashPassword(string password)
    {
        return Convert.ToHexString(
            System.Security.Cryptography.SHA256.HashData(
                System.Text.Encoding.UTF8.GetBytes(password)));
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserService](/csharp/complex/Services/UserService.md) |
