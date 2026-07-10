---
concept_id: typescript/complex/services/user-service/getUser
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
timestamp: '2026-07-10T14:55:12Z'
title: getUser
type: Function
---

# getUser

## Signature

```typescript
getUser(id: string): User | undefined
```

## Source
Lines 92–94 in `typescript/complex/services/user-service.ts`

```ts
  getUser(id: string): User | undefined {
    return this.repo.findById(id);
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserService *(unresolved)* |
