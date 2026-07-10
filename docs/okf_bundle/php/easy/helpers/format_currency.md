---
concept_id: php/easy/helpers/format_currency
description: Format a number as currency.
language: php
okf_version: '0.2'
resource: php/easy/helpers.php
tags:
- lang:php
- type:Function
- module:php
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: format_currency
type: Function
---

# format_currency

Format a number as currency.

## Signature

```php
function format_currency(float $amount, string $currency = 'USD'): string
```

## Docstring

Format a number as currency.

## Source
Lines 13–15 in `php/easy/helpers.php`

```php
function format_currency(float $amount, string $currency = 'USD'): string {
    return $currency . ' ' . number_format($amount, 2);
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [helpers](/php/easy/helpers.md) |
