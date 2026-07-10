---
concept_id: go/complex/handlers/user/CreateUser
description: CreateUser returns an HTTP handler that creates a new user.
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
timestamp: '2026-07-07T06:58:41Z'
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

```go
func CreateUser(s *store.UserStore) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var input store.CreateUserInput
		if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
			http.Error(w, `{"error":"invalid request body"}`, http.StatusBadRequest)
			return
		}
		user, err := s.Create(input)
		if err != nil {
			http.Error(w, `{"error":"`+err.Error()+`"}`, http.StatusBadRequest)
			return
		}
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(user)
	}
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/handlers/user.md) |
| calls | [Create](/go/complex/store/user/Create.md) |
| called_by | [registerRoutes](/go/complex/server/server/registerRoutes.md) |
