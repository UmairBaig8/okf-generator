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
timestamp: '2026-07-10T17:59:43Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [db](/typescript/complex/utils/db.md) |
| calls | [delete](/typescript/complex/utils/db/delete.md) |
