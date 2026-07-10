---
concept_id: javascript/complex/server/start
description: Start the HTTP server.
language: javascript
okf_version: '0.2'
resource: javascript/complex/server.js
tags:
- lang:javascript
- type:Function
- module:javascript
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: start
type: Function
---

# start

Start the HTTP server.

## Signature

```javascript
start()
```

## Docstring

Start the HTTP server.
@returns {Promise<void>}

## Returns
`Promise<void>`

## Source
Lines 62–95 in `javascript/complex/server.js`

```js
  async start() {
    return new Promise((resolve, reject) => {
      this.server = http.createServer(async (req, res) => {
        res.setHeader('Content-Type', 'application/json');
        try {
          const authResult = authenticate(req);
          if (!authResult.ok) {
            res.statusCode = 401;
            res.end(JSON.stringify({ error: authResult.error }));
            return;
          }
          const routeKey = `${req.method} ${req.url.split('?')[0]}`;
          const handler = this.routes.get(routeKey);
          if (!handler) {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: 'Not found' }));
            return;
          }
          const body = await this._parseBody(req);
          const result = await handler({ ...req, body, user: authResult.user });
          res.statusCode = result.statusCode || 200;
          res.end(JSON.stringify(result.data || {}));
        } catch (err) {
          res.statusCode = 500;
          res.end(JSON.stringify({ error: err.message || 'Internal server error' }));
        }
      });
      this.server.listen(this.port, this.host, () => {
        console.log(`Server listening on ${this.host}:${this.port}`);
        resolve();
      });
      this.server.on('error', reject);
    });
  }
```

## Relationships

| Type | Target |
|------|--------|
| related | ApiServer *(unresolved)* |
| calls | [authenticate](/javascript/complex/middleware/auth/authenticate.md) |
| calls | [_parseBody](/javascript/complex/server/parseBody.md) |
