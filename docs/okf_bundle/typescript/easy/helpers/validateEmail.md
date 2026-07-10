---
concept_id: typescript/easy/helpers/validateEmail
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
timestamp: '2026-07-07T06:58:42Z'
title: validateEmail
type: Function
---

# validateEmail

## Signature

```typescript
function validateEmail(value: string): Email | null
```

## Source
Lines 33–37 in `typescript/easy/helpers.ts`

```ts
export function validateEmail(value: string): Email | null {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!re.test(value)) return null;
  return value as Email;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [helpers](/typescript/easy/helpers.md) |
| called_by | [UserService](/typescript/complex/services/user-service/UserService.md) |
| called_by | [createUser](/typescript/complex/services/user-service/createUser.md) |
