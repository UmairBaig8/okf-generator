---
concept_id: csharp/easy/Utils/Sha256Hex
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
timestamp: '2026-07-10T15:03:07Z'
title: Sha256Hex
type: Function
---

# Sha256Hex

## Signature

```csharp
Sha256Hex()
```

## Visibility

- `public`
- `static`

## Source
Lines 13–18 in `csharp/easy/Utils.cs`

```cs
    public static string Sha256Hex(string input)
    {
        var bytes = System.Security.Cryptography.SHA256.HashData(
            System.Text.Encoding.UTF8.GetBytes(input));
        return Convert.ToHexStringLower(bytes);
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Utils](/csharp/easy/Utils.md) |
