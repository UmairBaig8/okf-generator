---
concept_id: typescript/easy/helpers/withRetry
language: typescript
okf_version: '0.2'
resource: typescript/easy/helpers.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:59:38Z'
title: withRetry
type: Function
---

# withRetry

## Signature

```typescript
function withRetry(
  fn: () => Promise<T>,
  maxRetries: number = 3,
): Promise<T>
```

## Type Parameters

- `T`

## Source
Lines 90–106 in `typescript/easy/helpers.ts`

## Relationships

| Type | Target |
|------|--------|
| related | [helpers](/typescript/easy/helpers.md) |
