---
concept_id: python/complex/config/Settings
description: Central configuration object loaded from environment variables.
language: python
okf_version: '0.2'
resource: python/complex/config.py
tags:
- lang:python
- type:Class
- module:python
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T17:42:36Z'
title: Settings
type: Class
---

# Settings

Central configuration object loaded from environment variables.

## Decorators

- `dataclass`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `version` | `str` | `` |
| `debug` | `bool` | `` |
| `payment_gateway_key` | `str` | `` |
| `max_retries` | `int` | `` |
| `allowed_currencies` | `frozenset[str]` | `` |
| `environment` | `Environment` | `` |

## Docstring

Central configuration object loaded from environment variables.

Attributes:
    version: Application version string.
    debug: Enable debug-level logging and error detail.
    payment_gateway_key: Secret API key for the payment gateway.
    max_retries: Number of times to retry failed gateway calls.
    allowed_currencies: Set of ISO currency codes the service accepts.

## Methods

- `is_production`
- `is_currency_allowed`

## Source
Lines 18–53 in `python/complex/config.py`

## Relationships

| Type | Target |
|------|--------|
| related | [config](/python/complex/config.md) |
| related | [is_production](/python/complex/config/is_production.md) |
| related | [is_currency_allowed](/python/complex/config/is_currency_allowed.md) |
