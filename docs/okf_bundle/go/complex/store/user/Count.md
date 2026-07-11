---
concept_id: go/complex/store/user/Count
description: Count is a generic helper that returns the number of items in a map.
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
timestamp: '2026-07-11T20:17:16Z'
title: Count
type: Function
---

# Count

Count is a generic helper that returns the number of items in a map.

## Signature

```go
func Count(m map[K]V) int
```

## Type Parameters

- `K comparable`
- `V any`

## Docstring

Count is a generic helper that returns the number of items in a map.

## Source
Lines 78–80 in `go/complex/store/user.go`

## Relationships

| Type | Target |
|------|--------|
| related | [user](/go/complex/store/user.md) |
