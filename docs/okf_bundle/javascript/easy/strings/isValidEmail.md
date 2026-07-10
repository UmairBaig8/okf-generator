---
concept_id: javascript/easy/strings/isValidEmail
description: Test whether a string is a valid email address (simple check).
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
title: isValidEmail
type: Function
---

# isValidEmail

Test whether a string is a valid email address (simple check).

## Signature

```javascript
function isValidEmail(str)
```

## Docstring

Test whether a string is a valid email address (simple check).
@param {string} str - String to test.
@returns {boolean} True if the string looks like an email.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `str` | `string` | `—` |

## Returns
`boolean`

## Source
Lines 44–48 in `javascript/easy/strings.js`

```js
function isValidEmail(str) {
  if (!str) return false;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(str);
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [strings](/javascript/easy/strings.md) |
