---
concept_id: javascript/complex/middleware/auth/authenticate
description: Authenticate an incoming HTTP request using the Authorization header.
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
timestamp: '2026-07-10T14:57:28Z'
title: authenticate
type: Function
---

# authenticate

Authenticate an incoming HTTP request using the Authorization header.

## Signature

```javascript
function authenticate(req)
```

## Docstring

Authenticate an incoming HTTP request using the Authorization header.
@param {object} req - The HTTP request object.
@param {string} [req.headers.authorization] - Bearer token.
@returns {{ok: boolean, user?: object, error?: string}} Auth result.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `req` | `object` | `—` |

| `[req.headers.authorization]` | `string` | `—` |

## Returns
`{ok: boolean, user?: object, error?: string`

## Source
Lines 17–33 in `javascript/complex/middleware/auth.js`

```js
function authenticate(req) {
  const authHeader = req.headers && req.headers.authorization;
  if (!authHeader) {
    return { ok: false, error: 'Missing Authorization header' };
  }
  if (!VALID_TOKENS.has(authHeader)) {
    return { ok: false, error: 'Invalid or expired token' };
  }
  const role = authHeader.includes('admin') ? 'admin' : 'user';
  return {
    ok: true,
    user: {
      id: authHeader === 'Bearer token-admin-001' ? 1 : 2,
      role,
    },
  };
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [auth](/javascript/complex/middleware/auth.md) |
| called_by | [ApiServer](/javascript/complex/server/ApiServer.md) |
| called_by | [start](/javascript/complex/server/start.md) |
