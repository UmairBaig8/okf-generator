---
concept_id: ruby/easy/math_helper/clamp
language: ruby
okf_version: '0.2'
resource: ruby/easy/math_helper.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:easy
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: clamp
type: Function
---

# clamp

## Signature

```ruby
def clamp(value, min, max)
```

## Source
Lines 41–43 in `ruby/easy/math_helper.rb`

```rb
  def clamp(value, min, max)
    [[value, min].max, max].min
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [math_helper](/ruby/easy/math_helper.md) |
