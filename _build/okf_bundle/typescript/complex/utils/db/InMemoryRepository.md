---
resource: typescript/complex/utils/db.ts
tags:
- lang:typescript
- type:Class
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:02Z'
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

## Related

- [db](/typescript/complex/utils/db.md)

## Calls

- [delete](/typescript/complex/utils/db/delete.md)
