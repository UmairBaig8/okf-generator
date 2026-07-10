---
concept_id: go/complex/store/user/Create
description: Create inserts a new user and returns it with an auto-generated ID.
language: go
okf_version: '0.2'
resource: go/complex/store/user.go
tags:
- lang:go
- type:Function
- module:go
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: Create
type: Function
---

# Create

Create inserts a new user and returns it with an auto-generated ID.

## Signature

```go
func (s *UserStore) Create(input CreateUserInput) (User, error)
```

## Docstring

Create inserts a new user and returns it with an auto-generated ID.

## Source
Lines 62–75 in `go/complex/store/user.go`

```go
func (s *UserStore) Create(input CreateUserInput) (User, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	id := fmt.Sprintf("u_%d", s.next)
	s.next++
	user := User{
		ID:        id,
		Name:      input.Name,
		Email:     input.Email,
		CreatedAt: time.Now().UTC(),
	}
	s.users[id] = user
	return user, nil
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/store/user.md) |
| called_by | [CreateUser](/go/complex/handlers/user/CreateUser.md) |
