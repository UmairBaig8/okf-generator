---
description: Verify that the authenticated user has a specific role.
resource: javascript/complex/middleware/auth.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:45Z'
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

## Related

- [auth](/javascript/complex/middleware/auth.md)
