---
concept_id: csharp/easy/Utils/IsValidEmail
language: csharp
okf_version: '0.2'
resource: csharp/easy/Utils.cs
tags:
- lang:csharp
- type:Function
- module:csharp
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: IsValidEmail
type: Function
---

# IsValidEmail

## Signature

```csharp
IsValidEmail()
```

## Visibility

- `public`
- `static`

## Source
Lines 25–34 in `csharp/easy/Utils.cs`

```cs
    public static bool IsValidEmail(string email)
    {
        if (string.IsNullOrWhiteSpace(email))
            return false;
        var atIndex = email.IndexOf('@');
        if (atIndex <= 0 || atIndex == email.Length - 1)
            return false;
        var dotIndex = email.LastIndexOf('.');
        return dotIndex > atIndex + 1 && dotIndex < email.Length - 1;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Utils](/csharp/easy/Utils.md) |
