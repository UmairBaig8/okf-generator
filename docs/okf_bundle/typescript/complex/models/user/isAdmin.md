---
concept_id: typescript/complex/models/user/isAdmin
description: Check whether the user has administrative privileges.
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
timestamp: '2026-07-10T14:55:12Z'
title: isAdmin
type: Function
---

# isAdmin

Check whether the user has administrative privileges.

## Signature

```typescript
isAdmin(): boolean
```

## Visibility

- `public`

## Docstring

Check whether the user has administrative privileges.
@returns True if the user is an admin.

## Source
Lines 51–53 in `typescript/complex/models/user.ts`

```ts
  public isAdmin(): boolean {
    return this.role === UserRole.ADMIN;
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | User *(unresolved)* |
