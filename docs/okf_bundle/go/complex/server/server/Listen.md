---
concept_id: go/complex/server/server/Listen
description: Listen starts the HTTP server on the given address.
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
timestamp: '2026-07-07T06:58:41Z'
title: Listen
type: Function
---

# Listen

Listen starts the HTTP server on the given address.

## Signature

```go
func (s *Server) Listen(addr string) error
```

## Docstring

Listen starts the HTTP server on the given address.

## Source
Lines 49–57 in `go/complex/server/server.go`

```go
func (s *Server) Listen(addr string) error {
	s.httpServer = &http.Server{
		Addr:         addr,
		Handler:      s.mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}
	return s.httpServer.ListenAndServe()
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [server](/go/complex/server/server.md) |
