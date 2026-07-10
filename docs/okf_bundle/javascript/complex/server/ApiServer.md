---
concept_id: javascript/complex/server/ApiServer
description: Simple request router that dispatches to route handlers.
language: javascript
okf_version: '0.2'
resource: javascript/complex/server.js
tags:
- lang:javascript
- type:Class
- module:javascript
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: ApiServer
type: Class
---

# ApiServer

Simple request router that dispatches to route handlers.

## Signature

```javascript
class ApiServer
```

## Docstring

Simple request router that dispatches to route handlers.
@extends http.Server

## Methods

- `constructor`
- `_registerRoutes`
- `_parseBody`
- `start`
- `stop`

## Source
Lines 16–114 in `javascript/complex/server.js`

## Relationships

| Type | Target |
|------|--------|
| related | [server](/javascript/complex/server.md) |
| calls | [_registerRoutes](/javascript/complex/server/registerRoutes.md) |
| calls | [toString](/java/easy/model/User/toString.md) |
| calls | [authenticate](/javascript/complex/middleware/auth/authenticate.md) |
| calls | [_parseBody](/javascript/complex/server/parseBody.md) |
