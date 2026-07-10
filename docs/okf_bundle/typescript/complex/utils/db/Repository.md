---
concept_id: typescript/complex/utils/db/Repository
language: typescript
okf_version: '0.2'
resource: typescript/complex/utils/db.ts
tags:
- lang:typescript
- type:Interface
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: Repository
type: Interface
---

# Repository

## Signature

```typescript
interface Repository
```

## Methods

- `findById`
- `findAll`
- `insert`
- `update`
- `delete`

## Source
Lines 10–16 in `typescript/complex/utils/db.ts`

```ts
export interface Repository<T extends { id: string }> {
  findById(id: string): T | undefined;
  findAll(): T[];
  insert(entity: T): T;
  update(id: string, partial: Partial<T>): T | undefined;
  delete(id: string): boolean;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/typescript/complex/utils/db.md) |
