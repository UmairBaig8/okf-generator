---
description: Find entities matching a predicate.
resource: typescript/complex/utils/db.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:02Z'
title: findWhere
type: Function
---

# findWhere

Find entities matching a predicate.

## Signature

```typescript
findWhere(predicate: (item: T) => boolean): T[]
```

## Docstring

Find entities matching a predicate.
@param predicate - Filter function.
@returns Matching entities.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `predicate` | `—` | `—` |

## Source
Lines 63–65 in `typescript/complex/utils/db.ts`

## Related

- InMemoryRepository *(unresolved)*

## Called By

- [UserService](/typescript/complex/services/user-service/UserService.md)
- [findUsersByRole](/typescript/complex/services/user-service/findUsersByRole.md)
