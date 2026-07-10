---
concept_id: typescript/complex/services/user-service/deleteUser
language: typescript
okf_version: '0.2'
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: deleteUser
type: Function
---

# deleteUser

## Signature

```typescript
deleteUser(id: string): boolean
```

## Source
Lines 126–128 in `typescript/complex/services/user-service.ts`

```ts
  deleteUser(id: string): boolean {
    return this.repo.delete(id);
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserService *(unresolved)* |
