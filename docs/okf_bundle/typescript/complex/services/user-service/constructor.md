---
concept_id: typescript/complex/services/user-service/constructor
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
timestamp: '2026-07-10T17:15:25Z'
title: constructor
type: Function
---

# constructor

## Signature

```typescript
constructor(repo?: InMemoryRepository<User>)
```

## Source
Lines 60–62 in `typescript/complex/services/user-service.ts`

```ts
  constructor(repo?: InMemoryRepository<User>) {
    this.repo = repo ?? new InMemoryRepository<User>();
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserService *(unresolved)* |
