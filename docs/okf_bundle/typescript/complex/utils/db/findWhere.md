---
concept_id: typescript/complex/utils/db/findWhere
description: Find entities matching a predicate.
language: typescript
okf_version: '0.2'
resource: typescript/complex/utils/db.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:04:24Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | InMemoryRepository *(unresolved)* |
| called_by | [UserService](/typescript/complex/services/user-service/UserService.md) |
| called_by | [findUsersByRole](/typescript/complex/services/user-service/findUsersByRole.md) |
