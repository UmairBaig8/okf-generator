---
concept_id: typescript/easy/helpers/paginate
language: typescript
okf_version: '0.2'
resource: typescript/easy/helpers.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: paginate
type: Function
---

# paginate

## Signature

```typescript
function paginate(items: T[], params: PaginationParams): PaginatedResponse<T>
```

## Type Parameters

- `T`

## Source
Lines 14–26 in `typescript/easy/helpers.ts`

## Relationships

| Type | Target |
|------|--------|
| related | [helpers](/typescript/easy/helpers.md) |
| called_by | [UserService](/typescript/complex/services/user-service/UserService.md) |
| called_by | [listUsers](/typescript/complex/services/user-service/listUsers.md) |
