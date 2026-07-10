---
concept_id: typescript/complex/utils/db/findById
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
title: findById
type: Function
---

# findById

## Signature

```typescript
findById(id: string): T | undefined
```

## Source
Lines 25–27 in `typescript/complex/utils/db.ts`

```ts
  findById(id: string): T | undefined {
    return this.items.get(id);
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | InMemoryRepository *(unresolved)* |
