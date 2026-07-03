---
description: registerRoutes attaches all API endpoints to the mux.
resource: go/complex/server/server.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:21Z'
title: registerRoutes
type: Function
---

# registerRoutes

registerRoutes attaches all API endpoints to the mux.

## Signature

```go
func (s *Server) registerRoutes()
```

## Docstring

registerRoutes attaches all API endpoints to the mux.

## Source
Lines 32–36 in `go/complex/server/server.go`

## Related

- [server](/go/complex/server/server.md)

## Calls

- [wrap](/go/complex/server/server/wrap.md)
- [ListUsers](/go/complex/handlers/user/ListUsers.md)
- [GetUser](/go/complex/handlers/user/GetUser.md)
- [CreateUser](/go/complex/handlers/user/CreateUser.md)

## Called By

- [NewServer](/go/complex/server/server/NewServer.md)
