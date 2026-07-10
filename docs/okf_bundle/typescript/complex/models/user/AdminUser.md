---
concept_id: typescript/complex/models/user/AdminUser
language: typescript
okf_version: '0.2'
resource: typescript/complex/models/user.ts
tags:
- lang:typescript
- type:Class
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:12Z'
title: AdminUser
type: Class
---

# AdminUser

## Signature

```typescript
class AdminUser
```

## Inheritance

- `User`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `permissions` | `string[]` | `public readonly` |

## Methods

- `constructor`
- `grantPermission`

## Source
Lines 75–97 in `typescript/complex/models/user.ts`

```ts
export class AdminUser extends User {
  public readonly permissions: string[];

  constructor(
    id: string,
    email: Email,
    name: string,
    permissions: string[] = ['read', 'write', 'delete', 'manage'],
  ) {
    super(id, email, name, UserRole.ADMIN);
    this.permissions = permissions;
  }

  /**
   * Grant an additional permission to this admin user.
   * @param permission - Permission string to add.
   */
  public grantPermission(permission: string): void {
    if (!this.permissions.includes(permission)) {
      this.permissions.push(permission);
    }
  }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/typescript/complex/models/user.md) |
