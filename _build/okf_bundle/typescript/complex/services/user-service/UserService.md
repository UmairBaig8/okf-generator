---
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Class
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:09Z'
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

## Related

- [user-service](/typescript/complex/services/user-service.md)

## Calls

- [Route](/typescript/complex/services/user-service/Route.md)
- [validateEmail](/typescript/easy/helpers/validateEmail.md)
- [randomString](/typescript/easy/helpers/randomString.md)
- [paginate](/typescript/easy/helpers/paginate.md)
- [update](/typescript/complex/utils/db/update.md)
- [findWhere](/typescript/complex/utils/db/findWhere.md)
