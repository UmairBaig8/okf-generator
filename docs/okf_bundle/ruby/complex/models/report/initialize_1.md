---
concept_id: ruby/complex/models/report/initialize_1
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
timestamp: '2026-07-10T14:57:28Z'
title: initialize
type: Function
---

# initialize

## Signature

```ruby
def initialize(id, title, schedule, data = {})
```

## Source
Lines 46–50 in `ruby/complex/models/report.rb`

```rb
    def initialize(id, title, schedule, data = {})
      super(id, title, data)
      @schedule = schedule
      @last_run = nil
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
