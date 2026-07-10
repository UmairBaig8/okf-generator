---
concept_id: javascript/easy/math/approxEqual
description: Check if a number is approximately equal to another within a tolerance.
language: javascript
okf_version: '0.2'
resource: javascript/easy/math.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T20:13:04Z'
title: approxEqual
type: Function
---

# approxEqual

Check if a number is approximately equal to another within a tolerance.

## Signature

```javascript
function approxEqual(a, b, epsilon = 1e-10)
```

## Docstring

Check if a number is approximately equal to another within a tolerance.
@param {number} a - First number.
@param {number} b - Second number.
@param {number} [epsilon=1e-10] - Comparison tolerance.
@returns {boolean} True if the numbers are approximately equal.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `a` | `number` | `—` |

| `b` | `number` | `—` |

| `[epsilon=1e-10]` | `number` | `—` |

## Returns
`boolean`

## Source
Lines 70–72 in `javascript/easy/math.js`

## Relationships

| Type | Target |
|------|--------|
| related | [math](/javascript/easy/math.md) |
