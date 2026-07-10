---
concept_id: typescript/easy/helpers/randomString
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
timestamp: '2026-07-10T14:55:12Z'
title: randomString
type: Function
---

# randomString

## Signature

```typescript
function randomString(length: number): string
```

## Source
Lines 75–82 in `typescript/easy/helpers.ts`

```ts
export function randomString(length: number): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [helpers](/typescript/easy/helpers.md) |
| called_by | [UserService](/typescript/complex/services/user-service/UserService.md) |
| called_by | [createUser](/typescript/complex/services/user-service/createUser.md) |
