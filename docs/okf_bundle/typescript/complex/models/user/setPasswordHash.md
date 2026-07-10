---
concept_id: typescript/complex/models/user/setPasswordHash
description: Set the user's password by storing a bcrypt-style hash.
language: typescript
okf_version: '0.2'
resource: typescript/complex/models/user.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:35:36Z'
title: setPasswordHash
type: Function
---

# setPasswordHash

Set the user's password by storing a bcrypt-style hash.

## Signature

```typescript
setPasswordHash(hash: string): void
```

## Visibility

- `public`

## Docstring

Set the user's password by storing a bcrypt-style hash.
@param hash - Pre-computed password hash.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `hash` | `—` | `—` |

## Source
Lines 42–45 in `typescript/complex/models/user.ts`

## Relationships

| Type | Target |
|------|--------|
| related | User *(unresolved)* |
