---
concept_id: typescript/complex/models/user/User
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
timestamp: '2026-07-10T15:03:07Z'
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

```ts
export class User {
  public readonly id: string;
  public readonly email: Email;
  public name: string;
  public role: UserRole;
  public address: Address | null;
  private _passwordHash: string;
  protected createdAt: Date;
  protected updatedAt: Date;

  constructor(
    id: string,
    email: Email,
    name: string,
    role: UserRole = UserRole.USER,
    address: Address | null = null,
  ) {
    this.id = id;
    this.email = email;
    this.name = name;
    this.role = role;
    this.address = address;
    this._passwordHash = '';
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  /**
   * Set the user's password by storing a bcrypt-style hash.
   * @param hash - Pre-computed password hash.
   */
  public setPasswordHash(hash: string): void {
    this._passwordHash = hash;
    this.updatedAt = new Date();
  }

  /**
   * Check whether the user has administrative privileges.
   * @returns True if the user is an admin.
   */
  public isAdmin(): boolean {
    return this.role === UserRole.ADMIN;
  }

  /**
   * Serialize the user to a plain object, excluding the password hash.
   * @returns Public user data.
   */
  public toJSON(): Record<string, unknown> {
    return {
      id: this.id,
      email: this.email,
      name: this.name,
      role: this.role,
      address: this.address,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
    };
  }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/typescript/complex/models/user.md) |
