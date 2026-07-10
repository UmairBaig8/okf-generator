---
concept_id: typescript/complex/services/user-service/UserService
language: typescript
okf_version: '0.2'
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Class
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:42Z'
title: UserService
type: Class
---

# UserService

## Signature

```typescript
class UserService
```

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `repo` | `InMemoryRepository<User>` | `private` |

## Methods

- `constructor`
- `createUser`
- `getUser`
- `listUsers`
- `updateUser`
- `deleteUser`
- `findUsersByRole`

## Source
Lines 57–138 in `typescript/complex/services/user-service.ts`

```ts
export class UserService {
  private repo: InMemoryRepository<User>;

  constructor(repo?: InMemoryRepository<User>) {
    this.repo = repo ?? new InMemoryRepository<User>();
  }

  /**
   * Create a new user after validating input.
   * @param dto - User creation data.
   * @returns The newly created User entity.
   * @throws If email validation fails.
   */
  @Logged
  @Route('POST', '/api/users')
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

  /**
   * Retrieve a user by ID.
   * @param id - User identifier.
   * @returns The user, or undefined.
   */
  @Route('GET', '/api/users/:id')
  getUser(id: string): User | undefined {
    return this.repo.findById(id);
  }

  /**
   * List all users with optional pagination.
   * @param page - Page number (1-indexed).
   * @param pageSize - Items per page.
   * @returns Paginated list of users.
   */
  @Route('GET', '/api/users')
  listUsers(page: number = 1, pageSize: number = 20): PaginatedResponse<User> {
    const all = this.repo.findAll();
    return paginate(all, { page, pageSize });
  }

  /**
   * Update user fields.
   * @param id - User identifier.
   * @param dto - Fields to update.
   * @returns The updated user, or undefined if not found.
   */
  @Logged
  @Route('PATCH', '/api/users/:id')
  updateUser(id: string, dto: UpdateUserDto): User | undefined {
    return this.repo.update(id, dto as Partial<User>);
  }

  /**
   * Remove a user from the system.
   * @param id - User identifier.
   * @returns True if the user was deleted.
   */
  @Route('DELETE', '/api/users/:id')
  deleteUser(id: string): boolean {
    return this.repo.delete(id);
  }

  /**
   * Find users matching a role.
   * @param role - Target role.
   * @returns Array of users with the given role.
   */
  findUsersByRole(role: UserRole): User[] {
    return this.repo.findWhere((u) => u.role === role);
  }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user-service](/typescript/complex/services/user-service.md) |
| calls | [Route](/typescript/complex/services/user-service/Route.md) |
| calls | [validateEmail](/typescript/easy/helpers/validateEmail.md) |
| calls | [randomString](/typescript/easy/helpers/randomString.md) |
| calls | [paginate](/typescript/easy/helpers/paginate.md) |
| calls | [update](/typescript/complex/utils/db/update.md) |
| calls | [findWhere](/typescript/complex/utils/db/findWhere.md) |
