---
concept_id: csharp/complex/Services/UserService/VerifyPassword
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
timestamp: '2026-07-10T14:57:28Z'
title: VerifyPassword
type: Function
---

# VerifyPassword

## Signature

```csharp
VerifyPassword()
```

## Visibility

- `private`
- `static`

## Source
Lines 61–64 in `csharp/complex/Services/UserService.cs`

```cs
    private static bool VerifyPassword(string password, string hash)
    {
        return HashPassword(password) == hash;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserService](/csharp/complex/Services/UserService.md) |
