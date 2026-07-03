---
description: GetUser returns an HTTP handler that fetches a single user by ID.
resource: go/complex/handlers/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:43:24Z'
title: GetUser
type: Function
---

# GetUser

GetUser returns an HTTP handler that fetches a single user by ID.

## Signature

```go
func GetUser(s *store.UserStore) http.HandlerFunc
```

## Docstring

GetUser returns an HTTP handler that fetches a single user by ID.

## Source
Lines 25–36 in `go/complex/handlers/user.go`

## Related

- [user](/go/complex/handlers/user.md)

## Calls

- [Get](/go/complex/store/user/Get.md)

## Called By

- [registerRoutes](/go/complex/server/server/registerRoutes.md)
