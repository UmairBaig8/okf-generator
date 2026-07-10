---
concept_id: javascript/complex/server/constructor
description: Create a new ApiServer instance.
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
title: constructor
type: Function
---

# constructor

Create a new ApiServer instance.

## Signature

```javascript
constructor(options = {})
```

## Docstring

Create a new ApiServer instance.
@param {object} [options] - Server configuration.
@param {number} [options.port=3000] - Listening port.
@param {string} [options.host='0.0.0.0'] - Binding address.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `[options]` | `object` | `—` |

| `[options.port=3000]` | `number` | `—` |

| `[options.host='0.0.0.0']` | `string` | `—` |

## Source
Lines 23–29 in `javascript/complex/server.js`

```js
  constructor(options = {}) {
    this.port = options.port || PORT;
    this.host = options.host || '0.0.0.0';
    this.routes = new Map();
    this.server = null;
    this._registerRoutes();
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | ApiServer *(unresolved)* |
| calls | [_registerRoutes](/javascript/complex/server/registerRoutes.md) |
