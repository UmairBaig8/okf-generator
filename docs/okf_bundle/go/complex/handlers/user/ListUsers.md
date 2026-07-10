---
concept_id: go/complex/handlers/user/ListUsers
description: ListUsers returns an HTTP handler that lists all users from the store.
language: go
okf_version: '0.2'
resource: go/complex/handlers/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T19:08:02Z'
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

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/handlers/user.md) |
| calls | [List](/go/complex/store/user/List.md) |
| called_by | [registerRoutes](/go/complex/server/server/registerRoutes.md) |
