---
description: wrap applies common middleware (logging, JSON content-type) to a handler.
resource: go/complex/server/server.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:21Z'
title: wrap
type: Function
---

# wrap

wrap applies common middleware (logging, JSON content-type) to a handler.

## Signature

```go
func (s *Server) wrap(next http.HandlerFunc) http.HandlerFunc
```

## Docstring

wrap applies common middleware (logging, JSON content-type) to a handler.

## Source
Lines 39–46 in `go/complex/server/server.go`

## Related

- [server](/go/complex/server/server.md)

## Called By

- [registerRoutes](/go/complex/server/server/registerRoutes.md)
