---
concept_id: go/easy/math/math/Min
description: Min returns the smaller of two integers.
language: go
okf_version: '0.2'
resource: go/easy/math/math.go
tags:
- lang:go
- type:Function
- module:go
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:57:28Z'
title: Min
type: Function
---

# Min

Min returns the smaller of two integers.

## Signature

```go
func Min(a, b int) int
```

## Docstring

Min returns the smaller of two integers.

## Source
Lines 14–19 in `go/easy/math/math.go`

```go
func Min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/go/easy/math/math.md) |
