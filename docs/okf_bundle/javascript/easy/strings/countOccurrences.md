---
concept_id: javascript/easy/strings/countOccurrences
description: Count the number of occurrences of a substring within a string.
language: javascript
okf_version: '0.2'
resource: javascript/easy/strings.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: countOccurrences
type: Function
---

# countOccurrences

Count the number of occurrences of a substring within a string.

## Signature

```javascript
function countOccurrences(str, substr)
```

## Docstring

Count the number of occurrences of a substring within a string.
@param {string} str - The haystack.
@param {string} substr - The needle.
@returns {number} Occurrence count.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `str` | `string` | `—` |

| `substr` | `string` | `—` |

## Returns
`number`

## Source
Lines 56–65 in `javascript/easy/strings.js`

```js
function countOccurrences(str, substr) {
  if (!str || !substr) return 0;
  let count = 0;
  let pos = 0;
  while ((pos = str.indexOf(substr, pos)) !== -1) {
    count++;
    pos += substr.length;
  }
  return count;
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [strings](/javascript/easy/strings.md) |
