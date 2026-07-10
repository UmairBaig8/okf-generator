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
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
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

```ts
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (attempt < maxRetries - 1) {
        await new Promise((r) => setTimeout(r, Math.pow(2, attempt) * 100));
      }
    }
  }
  throw lastError;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [helpers](/typescript/easy/helpers.md) |
