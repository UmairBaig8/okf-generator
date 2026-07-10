---
concept_id: ruby/easy/formatter/truncate_1
language: ruby
okf_version: '0.2'
resource: ruby/easy/formatter.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:easy
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: truncate
type: Function
---

# truncate

## Signature

```ruby
def truncate(max_len = 60)
```

## Source
Lines 52–54 in `ruby/easy/formatter.rb`

```rb
  def truncate(max_len = 60)
    Formatter.truncate(@text, max_len)
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [formatter](/ruby/easy/formatter.md) |
