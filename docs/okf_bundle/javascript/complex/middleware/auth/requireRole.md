---
concept_id: javascript/complex/middleware/auth/requireRole
description: Verify that the authenticated user has a specific role.
language: javascript
okf_version: '0.2'
resource: javascript/complex/middleware/auth.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-16T08:14:30Z'
title: requireRole
type: Function
---

# requireRole

Verify that the authenticated user has a specific role.

## Signature

```javascript
function requireRole(user, requiredRole)
```

## Docstring

Verify that the authenticated user has a specific role.
@param {object} user - The authenticated user object.
@param {string} requiredRole - The role to check for.
@returns {boolean} True if the user has the required role.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `user` | `object` | `—` |

| `requiredRole` | `string` | `—` |

## Returns
`boolean`

## Source
Lines 41–43 in `javascript/complex/middleware/auth.js`

## Relationships

| Type | Target |
|------|--------|
| related | [auth](/javascript/complex/middleware/auth.md) |
