---
concept_id: javascript/easy/strings/truncate
description: Truncate a string to a maximum length, appending an ellipsis if truncated.
language: javascript
okf_version: '0.2'
resource: javascript/easy/strings.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T18:59:38Z'
title: truncate
type: Function
---

# truncate

Truncate a string to a maximum length, appending an ellipsis if truncated.

## Signature

```javascript
function truncate(str, maxLength = 80, ellipsis = '...')
```

## Docstring

Truncate a string to a maximum length, appending an ellipsis if truncated.
@param {string} str - Input text.
@param {number} [maxLength=80] - Maximum allowed length.
@param {string} [ellipsis='...'] - Suffix appended when truncated.
@returns {string} Truncated string.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `str` | `string` | `—` |

| `[maxLength=80]` | `number` | `—` |

| `[ellipsis='...']` | `string` | `—` |

## Returns
`string`

## Source
Lines 25–28 in `javascript/easy/strings.js`

## Relationships

| Type | Target |
|------|--------|
| related | [strings](/javascript/easy/strings.md) |
