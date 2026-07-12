---
concept_id: javascript/easy/math/lerp
description: Linear interpolation between two values.
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
timestamp: '2026-07-12T07:14:59Z'
title: lerp
type: Function
---

# lerp

Linear interpolation between two values.

## Signature

```javascript
function lerp(a, b, t)
```

## Docstring

Linear interpolation between two values.
@param {number} a - Start value.
@param {number} b - End value.
@param {number} t - Interpolation factor (0-1).
@returns {number} The interpolated value.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `a` | `number` | `—` |

| `b` | `number` | `—` |

| `t` | `number` | `—` |

## Returns
`number`

## Source
Lines 59–61 in `javascript/easy/math.js`

## Relationships

| Type | Target |
|------|--------|
| related | [math](/javascript/easy/math.md) |
| calls | [clamp](/javascript/easy/math/clamp.md) |
