---
concept_id: php/easy/User/getUsername
description: User account status enum.
language: php
okf_version: '0.2'
resource: php/easy/User.php
tags:
- lang:php
- type:Function
- module:php
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: getUsername
type: Function
---

# getUsername

User account status enum.

## Signature

```php
function getUsername(): string
```

## Visibility

- `public`

## Docstring

User account status enum.

## Source
Lines 24–26 in `php/easy/User.php`

```php
    public function getUsername(): string {
        return $this->username;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/easy/User.md) |
