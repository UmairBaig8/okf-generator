---
concept_id: typescript/easy/types/PaginatedResponse
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
timestamp: '2026-07-10T17:15:25Z'
title: PaginatedResponse
type: Interface
---

# PaginatedResponse

## Signature

```typescript
interface PaginatedResponse
```

## Methods

- `items`
- `total`
- `page`
- `pageSize`
- `hasMore`

## Source
Lines 19–25 in `typescript/easy/types.ts`

```ts
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [types](/typescript/easy/types.md) |
