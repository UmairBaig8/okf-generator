---
description: Knowledge index for go/complex/server/server
resource: go/complex/server/server
timestamp: '2026-07-12T07:15:35Z'
title: server
type: Index
---

# server

## Classs

- [Server](Server.md) — Server wraps an http.Server with route handlers and middleware.

## Functions

- [jsonResponse](jsonResponse.md) — jsonResponse writes a JSON-encoded response with the given status code.
- [Listen](Listen.md) — Listen starts the HTTP server on the given address.
- [NewServer](NewServer.md) — NewServer creates a new Server with the given store and default routes.
- [registerRoutes](registerRoutes.md) — registerRoutes attaches all API endpoints to the mux.
- [wrap](wrap.md) — wrap applies common middleware (logging, JSON content-type) to a handler.
