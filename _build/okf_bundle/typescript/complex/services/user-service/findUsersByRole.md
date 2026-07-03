---
description: Find users matching a role.
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:09Z'
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

## Related

- UserService *(unresolved)*

## Calls

- [findWhere](/typescript/complex/utils/db/findWhere.md)
