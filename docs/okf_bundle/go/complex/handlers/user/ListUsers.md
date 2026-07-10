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
timestamp: '2026-07-10T15:03:07Z'
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

```go
func ListUsers(s *store.UserStore) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		users, err := s.List()
		if err != nil {
			http.Error(w, `{"error":"failed to list users"}`, http.StatusInternalServerError)
			return
		}
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]any{"users": users, "count": len(users)})
	}
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/handlers/user.md) |
| calls | [List](/go/complex/store/user/List.md) |
| called_by | [registerRoutes](/go/complex/server/server/registerRoutes.md) |
