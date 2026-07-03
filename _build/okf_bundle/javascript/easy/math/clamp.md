---
description: Clamp a number between a minimum and maximum value.
resource: javascript/easy/math.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:29Z'
title: clamp
type: Function
---

# clamp

Clamp a number between a minimum and maximum value.

## Signature

```javascript
function clamp(value, min, max)
```

## Docstring

Clamp a number between a minimum and maximum value.
@param {number} value - The value to clamp.
@param {number} min - Lower bound.
@param {number} max - Upper bound.
@returns {number} The clamped value.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `value` | `number` | `—` |
| `min` | `number` | `—` |
| `max` | `number` | `—` |

## Returns
`number`

## Source
Lines 13–17 in `javascript/easy/math.js`

## Related

- [math](/javascript/easy/math.md)

## Called By

- [lerp](/javascript/easy/math/lerp.md)
