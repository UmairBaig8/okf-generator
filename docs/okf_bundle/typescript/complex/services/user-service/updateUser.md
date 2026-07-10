---
concept_id: typescript/complex/services/user-service/updateUser
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
timestamp: '2026-07-10T19:11:07Z'
title: updateUser
type: Function
---

# updateUser

## Signature

```typescript
updateUser(id: string, dto: UpdateUserDto): User | undefined
```

## Source
Lines 116–118 in `typescript/complex/services/user-service.ts`

## Relationships

| Type | Target |
|------|--------|
| related | UserService *(unresolved)* |
| calls | [update](/typescript/complex/utils/db/update.md) |
