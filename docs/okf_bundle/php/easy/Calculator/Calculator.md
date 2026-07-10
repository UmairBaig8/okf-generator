---
concept_id: php/easy/Calculator/Calculator
description: A simple calculator class.
language: php
okf_version: '0.2'
resource: php/easy/Calculator.php
tags:
- lang:php
- type:Class
- module:php
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:15:25Z'
title: Calculator
type: Class
---

# Calculator

A simple calculator class.

## Signature

```php
class Calculator
```

## Docstring

A simple calculator class.

## Methods

- `__construct`
- `add`
- `reset`
- `version`

## Source
Lines 8–30 in `php/easy/Calculator.php`

```php
class Calculator {
    private float $result = 0.0;

    public function __construct() {
        $this->result = 0.0;
    }

    /**
     * Add a number to the current result.
     */
    public function add(float $value): float {
        $this->result += $value;
        return $this->result;
    }

    public function reset(): void {
        $this->result = 0.0;
    }

    public static function version(): string {
        return '1.0.0';
    }
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [Calculator](/php/easy/Calculator.md) |
