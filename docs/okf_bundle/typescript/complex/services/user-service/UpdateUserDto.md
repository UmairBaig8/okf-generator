---
concept_id: typescript/complex/services/user-service/UpdateUserDto
language: typescript
okf_version: '0.2'
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Interface
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: UpdateUserDto
type: Interface
---

# UpdateUserDto

## Signature

```typescript
interface UpdateUserDto
```

## Methods

- `name`
- `role`
- `address`

## Source
Lines 47–51 in `typescript/complex/services/user-service.ts`

```ts
export interface UpdateUserDto {
  name?: string;
  role?: UserRole;
  address?: Address;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user-service](/typescript/complex/services/user-service.md) |
