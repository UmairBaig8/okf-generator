---
description: Create a new ApiServer instance.
resource: javascript/complex/server.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:39Z'
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

## Related

- ApiServer *(unresolved)*

## Calls

- [_registerRoutes](/javascript/complex/server/registerRoutes.md)
