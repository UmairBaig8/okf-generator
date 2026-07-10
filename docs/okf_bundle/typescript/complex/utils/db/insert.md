---
concept_id: typescript/complex/utils/db/insert
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
timestamp: '2026-07-10T15:03:07Z'
title: insert
type: Function
---

# insert

## Signature

```typescript
insert(entity: T): T
```

## Source
Lines 33–36 in `typescript/complex/utils/db.ts`

```ts
  insert(entity: T): T {
    this.items.set(entity.id, entity);
    return entity;
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | InMemoryRepository *(unresolved)* |
