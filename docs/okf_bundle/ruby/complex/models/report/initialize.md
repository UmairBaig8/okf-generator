---
concept_id: ruby/complex/models/report/initialize
language: ruby
okf_version: '0.2'
resource: ruby/complex/models/report.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: initialize
type: Function
---

# initialize

## Signature

```ruby
def initialize(id, title, data = {})
```

## Source
Lines 7–12 in `ruby/complex/models/report.rb`

```rb
    def initialize(id, title, data = {})
      @id = id
      @title = title
      @data = data
      @generated_at = Time.now.utc
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
