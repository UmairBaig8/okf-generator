---
concept_id: typescript/complex/services/user-service/findUsersByRole
description: Find users matching a role.
language: typescript
okf_version: '0.2'
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-16T08:14:30Z'
title: findUsersByRole
type: Function
---

# findUsersByRole

Find users matching a role.

## Signature

```typescript
findUsersByRole(role: UserRole): User[]
```

## Docstring

Find users matching a role.
@param role - Target role.
@returns Array of users with the given role.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `role` | `—` | `—` |

## Source
Lines 135–137 in `typescript/complex/services/user-service.ts`

## Relationships

| Type | Target |
|------|--------|
| related | UserService *(unresolved)* |
| calls | [findWhere](/typescript/complex/utils/db/findWhere.md) |
