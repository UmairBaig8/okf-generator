---
resource: typescript/complex/models/user.ts
tags:
- lang:typescript
- type:Class
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:00Z'
title: User
type: Class
---

# User

## Signature

```typescript
class User
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `id` | `string` | `public readonly` |
| `email` | `Email` | `public readonly` |
| `name` | `string` | `public` |
| `role` | `UserRole` | `public` |
| `address` | `Address | null` | `public` |
| `_passwordHash` | `string` | `private` |
| `createdAt` | `Date` | `protected` |
| `updatedAt` | `Date` | `protected` |

## Methods

- `constructor`
- `setPasswordHash`
- `isAdmin`
- `toJSON`

## Source
Lines 11–70 in `typescript/complex/models/user.ts`

## Related

- [user](/typescript/complex/models/user.md)
