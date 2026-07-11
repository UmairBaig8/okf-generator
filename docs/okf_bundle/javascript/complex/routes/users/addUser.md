---
concept_id: javascript/complex/routes/users/addUser
description: Add a new user to the in-memory store.
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
timestamp: '2026-07-11T09:09:13Z'
title: addUser
type: Function
---

# addUser

Add a new user to the in-memory store.

## Signature

```javascript
function addUser(userData)
```

## Docstring

Add a new user to the in-memory store.
@param {object} userData - User fields (name, email, role).
@param {string} userData.name - Full name.
@param {string} userData.email - Email address.
@param {string} [userData.role='user'] - User role.
@returns {{id: number, name: string, email: string, role: string}} The created user.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `userData` | `object` | `—` |

| `userData.name` | `string` | `—` |

| `userData.email` | `string` | `—` |

| `[userData.role='user']` | `string` | `—` |

## Returns
`{id: number, name: string, email: string, role: string`

## Source
Lines 49–59 in `javascript/complex/routes/users.js`

## Relationships

| Type | Target |
|------|--------|
| related | [users](/javascript/complex/routes/users.md) |
