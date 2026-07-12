---
concept_id: typescript/complex/models/user/constructor
language: typescript
okf_version: '0.2'
resource: typescript/complex/models/user.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-12T22:02:43Z'
title: constructor
type: Function
---

# constructor

## Signature

```typescript
constructor(
    id: string,
    email: Email,
    name: string,
    role: UserRole = UserRole.USER,
    address: Address | null = null,
  )
```

## Source
Lines 21–36 in `typescript/complex/models/user.ts`

## Relationships

| Type | Target |
|------|--------|
| related | User *(unresolved)* |
