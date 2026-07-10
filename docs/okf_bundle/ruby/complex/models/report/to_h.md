---
concept_id: ruby/complex/models/report/to_h
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
timestamp: '2026-07-10T15:03:07Z'
title: to_h
type: Function
---

# to_h

## Signature

```ruby
def to_h()
```

## Source
Lines 14–21 in `ruby/complex/models/report.rb`

```rb
    def to_h
      {
        id: @id,
        title: @title,
        data: @data,
        generated_at: @generated_at.iso8601
      }
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
