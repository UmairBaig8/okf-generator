---
concept_id: typescript/complex/services/user-service/UserService
language: typescript
okf_version: '0.2'
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Class
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:59:43Z'
title: UserService
type: Class
---

# UserService

## Signature

```typescript
class UserService
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `repo` | `InMemoryRepository<User>` | `private` |

## Methods

- `constructor`
- `createUser`
- `getUser`
- `listUsers`
- `updateUser`
- `deleteUser`
- `findUsersByRole`

## Source
Lines 57–138 in `typescript/complex/services/user-service.ts`

## Relationships

| Type | Target |
|------|--------|
| related | [user-service](/typescript/complex/services/user-service.md) |
| calls | [Route](/typescript/complex/services/user-service/Route.md) |
| calls | [validateEmail](/typescript/easy/helpers/validateEmail.md) |
| calls | [randomString](/typescript/easy/helpers/randomString.md) |
| calls | [paginate](/typescript/easy/helpers/paginate.md) |
| calls | [update](/typescript/complex/utils/db/update.md) |
| calls | [findWhere](/typescript/complex/utils/db/findWhere.md) |
