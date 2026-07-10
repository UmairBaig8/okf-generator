---
concept_id: typescript/easy/types/PaginationParams
language: typescript
okf_version: '0.2'
resource: typescript/easy/types.ts
tags:
- lang:typescript
- type:Interface
- module:typescript
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:12Z'
title: PaginationParams
type: Interface
---

# PaginationParams

## Signature

```typescript
interface PaginationParams
```

## Methods

- `page`
- `pageSize`

## Source
Lines 13–16 in `typescript/easy/types.ts`

```ts
export interface PaginationParams {
  page: number;
  pageSize: number;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [types](/typescript/easy/types.md) |
