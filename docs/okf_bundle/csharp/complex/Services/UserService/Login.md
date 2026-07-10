---
concept_id: csharp/complex/Services/UserService/Login
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
timestamp: '2026-07-07T06:58:41Z'
title: Login
type: Function
---

# Login

## Signature

```csharp
Login()
```

## Visibility

- `public`

## Source
Lines 41–47 in `csharp/complex/Services/UserService.cs`

```cs
    public User? Login(string email, string password)
    {
        var user = _users.FirstOrDefault(u => u.Email == email);
        if (user == null || !VerifyPassword(password, user.PasswordHash))
            return null;
        return user;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserService](/csharp/complex/Services/UserService.md) |
