---
concept_id: typescript/complex/services/user-service/createUser
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
timestamp: '2026-07-10T20:08:44Z'
title: createUser
type: Function
---

# createUser

## Signature

```typescript
createUser(dto: CreateUserDto): User
```

## Source
Lines 72–84 in `typescript/complex/services/user-service.ts`

## Relationships

| Type | Target |
|------|--------|
| related | UserService *(unresolved)* |
| calls | [validateEmail](/typescript/easy/helpers/validateEmail.md) |
| calls | [randomString](/typescript/easy/helpers/randomString.md) |
