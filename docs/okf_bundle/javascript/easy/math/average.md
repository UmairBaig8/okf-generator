---
concept_id: javascript/easy/math/average
description: Compute the arithmetic mean of an array of numbers.
language: javascript
okf_version: '0.2'
resource: javascript/easy/math.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: average
type: Function
---

# average

Compute the arithmetic mean of an array of numbers.

## Signature

```javascript
function average(numbers)
```

## Docstring

Compute the arithmetic mean of an array of numbers.
@param {number[]} numbers - Array of numeric values.
@returns {number} The mean average.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `numbers` | `number[]` | `—` |

## Returns
`number`

## Source
Lines 35–38 in `javascript/easy/math.js`

```js
function average(numbers) {
  if (numbers.length === 0) return 0;
  return numbers.reduce((sum, n) => sum + n, 0) / numbers.length;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/javascript/easy/math.md) |
| called_by | [standardDeviation](/javascript/easy/math/standardDeviation.md) |
