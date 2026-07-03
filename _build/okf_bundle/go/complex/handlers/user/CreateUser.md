---
description: CreateUser returns an HTTP handler that creates a new user.
resource: go/complex/handlers/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:24Z'
title: CreateUser
type: Function
---

# CreateUser

CreateUser returns an HTTP handler that creates a new user.

## Signature

```go
func CreateUser(s *store.UserStore) http.HandlerFunc
```

## Docstring

CreateUser returns an HTTP handler that creates a new user.

## Source
Lines 39–54 in `go/complex/handlers/user.go`

## Related

- [user](/go/complex/handlers/user.md)

## Calls

- [Create](/go/complex/store/user/Create.md)

## Called By

- [registerRoutes](/go/complex/server/server/registerRoutes.md)
