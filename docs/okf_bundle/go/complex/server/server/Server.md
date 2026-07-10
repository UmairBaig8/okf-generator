---
concept_id: go/complex/server/server/Server
description: Server wraps an http.Server with route handlers and middleware.
language: go
okf_version: '0.2'
resource: go/complex/server/server.go
tags:
- lang:go
- type:Class
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: Server
type: Class
---

# Server

Server wraps an http.Server with route handlers and middleware.

## Signature

```go
type Server struct
```

## Docstring

Server wraps an http.Server with route handlers and middleware.

## Methods

- `httpServer`
- `userStore`
- `mux`

## Source
Lines 15–19 in `go/complex/server/server.go`

```go
type Server struct {
	httpServer *http.Server
	userStore  *store.UserStore
	mux        *http.ServeMux
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [server](/go/complex/server/server.md) |
