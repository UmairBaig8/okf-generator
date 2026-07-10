---
concept_id: php/easy/User/getId
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
title: getId
type: Function
---

# getId

User account status enum.

## Signature

```php
function getId(): int
```

## Visibility

- `public`

## Docstring

User account status enum.

## Source
Lines 20–22 in `php/easy/User.php`

```php
    public function getId(): int {
        return $this->id;
    }
```

## Relationships

| Type | Target |
|------|--------|
| related | [User](/php/easy/User.md) |
