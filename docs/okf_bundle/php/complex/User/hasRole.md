---
concept_id: php/complex/User/hasRole
language: php
okf_version: '0.2'
resource: php/complex/User.php
tags:
- lang:php
- type:Function
- module:php
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: hasRole
type: Function
---

# hasRole

## Signature

```php
function hasRole(string $role): bool
```

## Visibility

- `public`

## Source
Lines 24–24 in `php/complex/User.php`

```php
    public function hasRole(string $role): bool { return in_array($role, $this->roles); }
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/complex/User.md) |
