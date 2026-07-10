---
concept_id: ruby/complex/models/report/to_json
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
timestamp: '2026-07-10T14:55:11Z'
title: to_json
type: Function
---

# to_json

## Signature

```ruby
def to_json()
```

## Source
Lines 34–37 in `ruby/complex/models/report.rb`

```rb
    def to_json
      require "json"
      to_h.to_json
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
| called_by | [Exportable](/ruby/complex/models/report/Exportable.md) |
| called_by | [Models](/ruby/complex/models/report/Models.md) |
