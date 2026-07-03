---
description: Parse the incoming HTTP request body as JSON.
resource: javascript/complex/server.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:42:39Z'
title: _parseBody
type: Function
---

# _parseBody

Parse the incoming HTTP request body as JSON.

## Signature

```javascript
_parseBody(req)
```

## Docstring

Parse the incoming HTTP request body as JSON.
@param {http.IncomingMessage} req - The request object.
@returns {Promise<object>} Parsed JSON body.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `req` | `http.IncomingMessage` | `—` |

## Returns
`Promise<object>`

## Source
Lines 41–56 in `javascript/complex/server.js`

## Related

- ApiServer *(unresolved)*

## Calls

- [toString](/java/easy/model/User/toString.md)

## Called By

- [ApiServer](/javascript/complex/server/ApiServer.md)
- [start](/javascript/complex/server/start.md)
