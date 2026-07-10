---
concept_id: go/complex/server/server/jsonResponse
description: jsonResponse writes a JSON-encoded response with the given status code.
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
timestamp: '2026-07-10T18:26:54Z'
title: jsonResponse
type: Function
---

# jsonResponse

jsonResponse writes a JSON-encoded response with the given status code.

## Signature

```go
func jsonResponse(w http.ResponseWriter, status int, data any)
```

## Docstring

jsonResponse writes a JSON-encoded response with the given status code.

## Source
Lines 60–63 in `go/complex/server/server.go`

## Relationships

| Type | Target |
|------|--------|
| related | [server](/go/complex/server/server.md) |
