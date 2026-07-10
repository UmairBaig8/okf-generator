---
concept_id: csharp/easy/Models/User/GetDisplayText
language: csharp
okf_version: '0.2'
resource: csharp/easy/Models/User.cs
tags:
- lang:csharp
- type:Function
- module:csharp
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: GetDisplayText
type: Function
---

# GetDisplayText

## Signature

```csharp
GetDisplayText()
```

## Visibility

- `public`

## Source
Lines 26–26 in `csharp/easy/Models/User.cs`

```cs
    public string GetDisplayText() => DisplayName ?? Email;
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/csharp/easy/Models/User.md) |
