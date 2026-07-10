---
concept_id: typescript/complex/services/user-service/createUser
language: typescript
okf_version: '0.2'
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: createUser
type: Function
---

# createUser

## Signature

```typescript
createUser(dto: CreateUserDto): User
```

## Source
Lines 72–84 in `typescript/complex/services/user-service.ts`

```ts
  createUser(dto: CreateUserDto): User {
    const email = validateEmail(dto.email);
    if (!email) {
      throw new Error(`Invalid email address: ${dto.email}`);
    }
    const id = `user_${randomString(12)}`;
    const role = dto.role ?? UserRole.USER;
    const user: User = role === UserRole.ADMIN
      ? new AdminUser(id, email, dto.name)
      : new User(id, email, dto.name, role, dto.address ?? null);
    this.repo.insert(user);
    return user;
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | UserService *(unresolved)* |
| calls | [validateEmail](/typescript/easy/helpers/validateEmail.md) |
| calls | [randomString](/typescript/easy/helpers/randomString.md) |
