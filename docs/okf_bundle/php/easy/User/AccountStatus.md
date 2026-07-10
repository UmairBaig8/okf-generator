---
concept_id: php/easy/User/AccountStatus
description: User account status enum.
language: php
okf_version: '0.2'
resource: php/easy/User.php
tags:
- lang:php
- type:Enum
- module:php
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: AccountStatus
type: Enum
---

# AccountStatus

User account status enum.

## Signature

```php
enum AccountStatus
```

## Docstring

User account status enum.

## Methods

- `ACTIVE`
- `INACTIVE`
- `BANNED`
- `PENDING`

## Source
Lines 61–66 in `php/easy/User.php`

```php
enum AccountStatus: string {
    case ACTIVE = 'active';
    case INACTIVE = 'inactive';
    case BANNED = 'banned';
    case PENDING = 'pending';
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/easy/User.md) |
