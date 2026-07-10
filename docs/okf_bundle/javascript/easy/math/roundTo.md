---
concept_id: javascript/easy/math/roundTo
description: Round a number to a specified number of decimal places.
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
timestamp: '2026-07-07T06:58:41Z'
title: roundTo
type: Function
---

# roundTo

Round a number to a specified number of decimal places.

## Signature

```javascript
function roundTo(value, decimals = 2)
```

## Docstring

Round a number to a specified number of decimal places.
@param {number} value - The value to round.
@param {number} [decimals=2] - Number of decimal places.
@returns {number} The rounded value.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `value` | `number` | `—` |

| `[decimals=2]` | `number` | `—` |

## Returns
`number`

## Source
Lines 25–28 in `javascript/easy/math.js`

```js
function roundTo(value, decimals = 2) {
  const factor = Math.pow(10, decimals);
  return Math.round(value * factor) / factor;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/javascript/easy/math.md) |
| calls | [round](/ruby/easy/math_helper/round.md) |
