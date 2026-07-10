---
concept_id: go/complex/server/server/NewServer
description: NewServer creates a new Server with the given store and default routes.
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
timestamp: '2026-07-10T17:15:25Z'
title: NewServer
type: Function
---

# NewServer

NewServer creates a new Server with the given store and default routes.

## Signature

```go
func NewServer(userStore *store.UserStore) *Server
```

## Docstring

NewServer creates a new Server with the given store and default routes.

## Source
Lines 22–29 in `go/complex/server/server.go`

```go
func NewServer(userStore *store.UserStore) *Server {
	s := &Server{
		userStore: userStore,
		mux:       http.NewServeMux(),
	}
	s.registerRoutes()
	return s
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [server](/go/complex/server/server.md) |
| calls | [registerRoutes](/go/complex/server/server/registerRoutes.md) |
