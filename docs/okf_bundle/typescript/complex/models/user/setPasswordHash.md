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
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
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

```ts
  public setPasswordHash(hash: string): void {
    this._passwordHash = hash;
    this.updatedAt = new Date();
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | User *(unresolved)* |
