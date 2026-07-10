---
concept_id: csharp/easy/Utils/Truncate
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
title: Truncate
type: Function
---

# Truncate

## Signature

```csharp
Truncate()
```

## Visibility

- `public`
- `static`

## Source
Lines 42–47 in `csharp/easy/Utils.cs`

```cs
    public static string Truncate(string text, int maxLength)
    {
        if (string.IsNullOrEmpty(text) || text.Length <= maxLength)
            return text;
        return text[..(maxLength - 3)] + "...";
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [Utils](/csharp/easy/Utils.md) |
