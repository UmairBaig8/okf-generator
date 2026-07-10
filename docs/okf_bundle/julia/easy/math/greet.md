---
concept_id: julia/easy/math/greet
language: julia
okf_version: '0.2'
resource: julia/easy/math.jl
tags:
- lang:julia
- type:Function
- module:julia
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: greet
type: Function
---

# greet

## Signature

```julia
greet(name::String)::String
```

## Source
Lines 15–17 in `julia/easy/math.jl`

```jl
function greet(name::String)::String
    return "Hello, $name"
end
```

## Relationships

| Type | Target |
|------|--------|
| related | [math](/julia/easy/math.md) |
