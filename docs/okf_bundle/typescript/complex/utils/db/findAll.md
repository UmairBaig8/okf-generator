---
concept_id: typescript/complex/utils/db/findAll
language: typescript
okf_version: '0.2'
resource: typescript/complex/utils/db.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: findAll
type: Function
---

# findAll

## Signature

```typescript
findAll(): T[]
```

## Source
Lines 29–31 in `typescript/complex/utils/db.ts`

```ts
  findAll(): T[] {
    return Array.from(this.items.values());
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | InMemoryRepository *(unresolved)* |
