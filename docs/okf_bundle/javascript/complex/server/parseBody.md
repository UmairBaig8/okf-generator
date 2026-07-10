---
concept_id: javascript/complex/server/parseBody
description: Parse the incoming HTTP request body as JSON.
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

```js
  _parseBody(req) {
    return new Promise((resolve, reject) => {
      let body = '';
      req.on('data', (chunk) => {
        body += chunk.toString();
      });
      req.on('end', () => {
        try {
          resolve(body ? JSON.parse(body) : {});
        } catch (err) {
          reject(new Error('Invalid JSON in request body'));
        }
      });
      req.on('error', reject);
    });
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | ApiServer *(unresolved)* |
| calls | [toString](/java/easy/model/User/toString.md) |
| called_by | [ApiServer](/javascript/complex/server/ApiServer.md) |
| called_by | [start](/javascript/complex/server/start.md) |
