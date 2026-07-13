---
concept_id: typescript/complex/services/user-service/listUsers
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
timestamp: '2026-07-13T20:34:09Z'
title: listUsers
type: Function
---

# listUsers

## Signature

```typescript
listUsers(page: number = 1, pageSize: number = 20): PaginatedResponse<User>
```

## Source
Lines 103–106 in `typescript/complex/services/user-service.ts`

## Relationships

| Type | Target |
|------|--------|
| related | UserService *(unresolved)* |
| calls | [paginate](/typescript/easy/helpers/paginate.md) |
