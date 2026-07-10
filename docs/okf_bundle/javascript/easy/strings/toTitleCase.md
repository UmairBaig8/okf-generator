---
concept_id: javascript/easy/strings/toTitleCase
description: Capitalize the first letter of each word in a string.
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
timestamp: '2026-07-10T14:55:11Z'
title: toTitleCase
type: Function
---

# toTitleCase

Capitalize the first letter of each word in a string.

## Signature

```javascript
function toTitleCase(str)
```

## Docstring

Capitalize the first letter of each word in a string.
@param {string} str - Input text.
@returns {string} Title-cased text.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `str` | `string` | `—` |

## Returns
`string`

## Source
Lines 11–16 in `javascript/easy/strings.js`

```js
function toTitleCase(str) {
  if (!str) return '';
  return str.replace(/\w\S*/g, (word) => {
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  });
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [strings](/javascript/easy/strings.md) |
