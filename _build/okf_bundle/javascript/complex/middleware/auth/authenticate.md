---
description: Authenticate an incoming HTTP request using the Authorization header.
resource: javascript/complex/middleware/auth.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:45Z'
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

## Related

- [auth](/javascript/complex/middleware/auth.md)

## Called By

- [ApiServer](/javascript/complex/server/ApiServer.md)
- [start](/javascript/complex/server/start.md)
