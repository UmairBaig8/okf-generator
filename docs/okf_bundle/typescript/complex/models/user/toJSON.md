---
concept_id: typescript/complex/models/user/toJSON
description: Serialize the user to a plain object, excluding the password hash.
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
title: toJSON
type: Function
---

# toJSON

Serialize the user to a plain object, excluding the password hash.

## Signature

```typescript
toJSON(): Record<string, unknown>
```

## Visibility

- `public`

## Docstring

Serialize the user to a plain object, excluding the password hash.
@returns Public user data.

## Source
Lines 59–69 in `typescript/complex/models/user.ts`

```ts
  public toJSON(): Record<string, unknown> {
    return {
      id: this.id,
      email: this.email,
      name: this.name,
      role: this.role,
      address: this.address,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
    };
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | User *(unresolved)* |
