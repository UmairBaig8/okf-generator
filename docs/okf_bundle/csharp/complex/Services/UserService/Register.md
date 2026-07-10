---
concept_id: csharp/complex/Services/UserService/Register
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
timestamp: '2026-07-10T14:55:11Z'
title: Register
type: Function
---

# Register

## Signature

```csharp
Register()
```

## Visibility

- `public`

## Source
Lines 17–33 in `csharp/complex/Services/UserService.cs`

```cs
    public User Register(string email, string password)
    {
        if (string.IsNullOrWhiteSpace(email))
            throw new ArgumentException("Email is required.");
        if (_users.Any(u => u.Email == email))
            throw new InvalidOperationException("Email already registered.");

        var user = new User
        {
            Id = $"u_{_nextId++}",
            Email = email,
            PasswordHash = HashPassword(password),
            CreatedAt = DateTime.UtcNow
        };
        _users.Add(user);
        return user;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserService](/csharp/complex/Services/UserService.md) |
