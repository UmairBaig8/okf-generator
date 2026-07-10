---
concept_id: javascript/complex/server/registerRoutes
description: Register the default API routes.
language: javascript
okf_version: '0.2'
resource: javascript/complex/server.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: _registerRoutes
type: Function
---

# _registerRoutes

Register the default API routes.

## Signature

```javascript
_registerRoutes()
```

## Docstring

Register the default API routes.

## Source
Lines 32–34 in `javascript/complex/server.js`

```js
  _registerRoutes() {
    this.routes.set('GET /api/users', handleUsersRoute);
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | ApiServer *(unresolved)* |
| called_by | [ApiServer](/javascript/complex/server/ApiServer.md) |
| called_by | [constructor](/javascript/complex/server/constructor.md) |
