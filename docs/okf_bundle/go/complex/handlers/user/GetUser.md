---
concept_id: go/complex/handlers/user/GetUser
description: GetUser returns an HTTP handler that fetches a single user by ID.
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
timestamp: '2026-07-10T14:55:11Z'
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

```go
func GetUser(s *store.UserStore) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		id := r.PathValue("id")
		user, err := s.Get(id)
		if err != nil {
			http.Error(w, `{"error":"user not found"}`, http.StatusNotFound)
			return
		}
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(user)
	}
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/handlers/user.md) |
| calls | [Get](/go/complex/store/user/Get.md) |
| called_by | [registerRoutes](/go/complex/server/server/registerRoutes.md) |
