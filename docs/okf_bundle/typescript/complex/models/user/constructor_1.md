---
concept_id: typescript/complex/models/user/constructor_1
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
timestamp: '2026-07-10T19:52:39Z'
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
    permissions: string[] = ['read', 'write', 'delete', 'manage'],
  )
```

## Source
Lines 78–86 in `typescript/complex/models/user.ts`

## Relationships

| Type | Target |
|------|--------|
| related | AdminUser *(unresolved)* |
