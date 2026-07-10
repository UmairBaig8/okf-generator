---
concept_id: typescript/easy/types/Address
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
title: Address
type: Interface
---

# Address

## Signature

```typescript
interface Address
```

## Methods

- `street`
- `city`
- `state`
- `zipCode`
- `country`

## Source
Lines 49–55 in `typescript/easy/types.ts`

```ts
export interface Address {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [types](/typescript/easy/types.md) |
