---
concept_id: typescript/complex/utils/db/InMemoryRepository
language: typescript
okf_version: '0.2'
resource: typescript/complex/utils/db.ts
tags:
- lang:typescript
- type:Class
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: InMemoryRepository
type: Class
---

# InMemoryRepository

## Signature

```typescript
class InMemoryRepository
```

## Type Parameters

- `T extends { id: string }`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `items` | `Map<string, T>` | `private` |

## Methods

- `findById`
- `findAll`
- `insert`
- `update`
- `delete`
- `count`
- `findWhere`

## Source
Lines 22–66 in `typescript/complex/utils/db.ts`

```ts
export class InMemoryRepository<T extends { id: string }> implements Repository<T> {
  private items: Map<string, T> = new Map();

  findById(id: string): T | undefined {
    return this.items.get(id);
  }

  findAll(): T[] {
    return Array.from(this.items.values());
  }

  insert(entity: T): T {
    this.items.set(entity.id, entity);
    return entity;
  }

  update(id: string, partial: Partial<T>): T | undefined {
    const existing = this.items.get(id);
    if (!existing) return undefined;
    const updated = { ...existing, ...partial, id } as T;
    this.items.set(id, updated);
    return updated;
  }

  delete(id: string): boolean {
    return this.items.delete(id);
  }

  /**
   * Count the number of entities in the collection.
   * @returns Entity count.
   */
  count(): number {
    return this.items.size;
  }

  /**
   * Find entities matching a predicate.
   * @param predicate - Filter function.
   * @returns Matching entities.
   */
  findWhere(predicate: (item: T) => boolean): T[] {
    return Array.from(this.items.values()).filter(predicate);
  }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [db](/typescript/complex/utils/db.md) |
| calls | [delete](/typescript/complex/utils/db/delete.md) |
