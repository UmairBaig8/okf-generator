---
concept_id: typescript/easy/types/ApiResponse
language: typescript
okf_version: '0.2'
resource: typescript/easy/types.ts
tags:
- lang:typescript
- type:Interface
- module:typescript
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: ApiResponse
type: Interface
---

# ApiResponse

## Signature

```typescript
interface ApiResponse
```

## Methods

- `success`
- `data`
- `error`
- `timestamp`

## Source
Lines 34–39 in `typescript/easy/types.ts`

```ts
export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
  timestamp: ISODateString;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [types](/typescript/easy/types.md) |
