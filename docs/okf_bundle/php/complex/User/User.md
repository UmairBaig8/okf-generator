---
concept_id: php/complex/User/User
language: php
okf_version: '0.2'
resource: php/complex/User.php
tags:
- lang:php
- type:Class
- module:php
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: User
type: Class
---

# User

## Signature

```php
class User
```

## Methods

- `__construct`
- `getId`
- `getUsername`
- `addRole`
- `hasRole`

## Source
Lines 7–25 in `php/complex/User.php`

```php
class User {
    private int $id;
    private string $username;
    private array $roles = [];

    public function __construct(int $id, string $username) {
        $this->id = $id;
        $this->username = $username;
    }

    public function getId(): int { return $this->id; }
    public function getUsername(): string { return $this->username; }
    public function addRole(string $role): void {
        if (!in_array($role, $this->roles)) {
            $this->roles[] = $role;
        }
    }
    public function hasRole(string $role): bool { return in_array($role, $this->roles); }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/complex/User.md) |
