---
concept_id: go/complex/server/server/wrap
description: wrap applies common middleware (logging, JSON content-type) to a handler.
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

```go
func (s *Server) wrap(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		w.Header().Set("Content-Type", "application/json")
		next(w, r)
		fmt.Printf("[%s] %s %s (%v)\n", r.Method, r.URL.Path, r.RemoteAddr, time.Since(start))
	}
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [server](/go/complex/server/server.md) |
| called_by | [registerRoutes](/go/complex/server/server/registerRoutes.md) |
