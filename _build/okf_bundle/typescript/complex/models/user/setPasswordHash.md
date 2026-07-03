---
description: Set the user's password by storing a bcrypt-style hash.
resource: typescript/complex/models/user.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:00Z'
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

## Related

- User *(unresolved)*
