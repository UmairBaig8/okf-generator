---
concept_id: ruby/complex/services/report_service/summary
description: Return a summary of all managed reports.
language: ruby
okf_version: '0.2'
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: summary
type: Function
---

# summary

Return a summary of all managed reports.

## Signature

```ruby
def summary()
```

## Docstring

Return a summary of all managed reports.

## Source
Lines 52–54 in `ruby/complex/services/report_service.rb`

```rb
    def summary
      @reports.map(&:summary)
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
