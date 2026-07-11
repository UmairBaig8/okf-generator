---
concept_id: go/complex/server/server/registerRoutes
description: registerRoutes attaches all API endpoints to the mux.
language: go
okf_version: '0.2'
resource: go/complex/server/server.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T20:17:16Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [server](/go/complex/server/server.md) |
| calls | [wrap](/go/complex/server/server/wrap.md) |
| calls | [ListUsers](/go/complex/handlers/user/ListUsers.md) |
| calls | [GetUser](/go/complex/handlers/user/GetUser.md) |
| calls | [CreateUser](/go/complex/handlers/user/CreateUser.md) |
| called_by | [NewServer](/go/complex/server/server/NewServer.md) |
