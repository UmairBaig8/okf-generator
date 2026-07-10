---
concept_id: typescript/complex/models/user/grantPermission
description: Grant an additional permission to this admin user.
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
timestamp: '2026-07-10T17:15:25Z'
title: grantPermission
type: Function
---

# grantPermission

Grant an additional permission to this admin user.

## Signature

```typescript
grantPermission(permission: string): void
```

## Visibility

- `public`

## Docstring

Grant an additional permission to this admin user.
@param permission - Permission string to add.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `permission` | `—` | `—` |

## Source
Lines 92–96 in `typescript/complex/models/user.ts`

```ts
  public grantPermission(permission: string): void {
    if (!this.permissions.includes(permission)) {
      this.permissions.push(permission);
    }
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | AdminUser *(unresolved)* |
