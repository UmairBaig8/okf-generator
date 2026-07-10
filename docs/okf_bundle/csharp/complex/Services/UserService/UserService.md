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
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
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

```cs
public class UserService
{
    private readonly List<User> _users = new();
    private int _nextId = 1;

    /// <summary>
    /// Registers a new user account.
    /// </summary>
    /// <param name="email">Email address.</param>
    /// <param name="password">Plain-text password (hashed before storage).</param>
    /// <returns>The created User.</returns>
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

    /// <summary>
    /// Authenticates a user by email and password.
    /// </summary>
    /// <param name="email">User's email.</param>
    /// <param name="password">Plain-text password.</param>
    /// <returns>The authenticated User, or null on failure.</returns>
    public User? Login(string email, string password)
    {
        var user = _users.FirstOrDefault(u => u.Email == email);
        if (user == null || !VerifyPassword(password, user.PasswordHash))
            return null;
        return user;
    }

    /// <summary>
    /// Returns all registered users.
    /// </summary>
    public IReadOnlyList<User> GetAllUsers() => _users.AsReadOnly();

    private static string HashPassword(string password)
    {
        return Convert.ToHexString(
            System.Security.Cryptography.SHA256.HashData(
                System.Text.Encoding.UTF8.GetBytes(password)));
    }

    private static bool VerifyPassword(string password, string hash)
    {
        return HashPassword(password) == hash;
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [UserService](/csharp/complex/Services/UserService.md) |
