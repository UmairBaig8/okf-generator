---
concept_id: javascript/complex/routes/users/handleUsersRoute
description: Handle GET /api/users requests.
language: javascript
okf_version: '0.2'
resource: javascript/complex/routes/users.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:08:02Z'
title: handleUsersRoute
type: Function
---

# handleUsersRoute

Handle GET /api/users requests.

## Signature

```javascript
function handleUsersRoute(req)
```

## Docstring

Handle GET /api/users requests.
Supports optional ?role= query parameter filtering.
@param {object} req - Extended request object with parsed body and user.
@param {object} req.query - URL query parameters.
@param {string} [req.query.role] - Filter by user role.
@param {object} req.user - Authenticated user from middleware.
@returns {Promise<{statusCode: number, data: object}>} API response.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `req` | `object` | `—` |

| `req.query` | `object` | `—` |

| `[req.query.role]` | `string` | `—` |

| `req.user` | `object` | `—` |

## Returns
`Promise<{statusCode: number, data: object`

## Source
Lines 24–39 in `javascript/complex/routes/users.js`

## Relationships

| Type | Target |
|------|--------|
| related | [users](/javascript/complex/routes/users.md) |
