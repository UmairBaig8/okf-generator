---
resource: typescript/easy/helpers.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:55Z'
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

## Related

- [helpers](/typescript/easy/helpers.md)
