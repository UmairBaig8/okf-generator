---
concept_id: ruby/complex/models/report/to_csv
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
title: to_csv
type: Function
---

# to_csv

## Signature

```ruby
def to_csv()
```

## Source
Lines 30–32 in `ruby/complex/models/report.rb`

```rb
    def to_csv
      @data.map { |row| row.values.join(",") }.join("\n")
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
