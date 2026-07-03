---
description: ListUsers returns an HTTP handler that lists all users from the store.
resource: go/complex/handlers/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:24Z'
title: ListUsers
type: Function
---

# ListUsers

ListUsers returns an HTTP handler that lists all users from the store.

## Signature

```go
func ListUsers(s *store.UserStore) http.HandlerFunc
```

## Docstring

ListUsers returns an HTTP handler that lists all users from the store.

## Source
Lines 12–22 in `go/complex/handlers/user.go`

## Related

- [user](/go/complex/handlers/user.md)

## Calls

- [List](/go/complex/store/user/List.md)

## Called By

- [registerRoutes](/go/complex/server/server/registerRoutes.md)
