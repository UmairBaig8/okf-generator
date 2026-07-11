---
concept_id: typescript/complex/utils/db/update
language: typescript
okf_version: '0.2'
resource: typescript/complex/utils/db.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T10:49:18Z'
title: update
type: Function
---

# update

## Signature

```typescript
update(id: string, partial: Partial<T>): T | undefined
```

## Source
Lines 38–44 in `typescript/complex/utils/db.ts`

## Relationships

| Type | Target |
|------|--------|
| related | InMemoryRepository *(unresolved)* |
| called_by | [compute_checksum](/python/easy/utils/compute_checksum.md) |
| called_by | [compute_checksum](/python/easy_v2/utils/compute_checksum.md) |
| called_by | [UserService](/typescript/complex/services/user-service/UserService.md) |
| called_by | [updateUser](/typescript/complex/services/user-service/updateUser.md) |
