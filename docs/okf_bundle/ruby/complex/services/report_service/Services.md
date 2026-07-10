---
concept_id: ruby/complex/services/report_service/Services
language: ruby
okf_version: '0.2'
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Class
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T20:22:11Z'
title: Services
type: Class
---

# Services

## Signature

```ruby
module Services
```

## Methods

- `initialize`
- `generate`
- `schedule`
- `find`
- `run_due`
- `summary`
- `next_id`
- `initialize`
- `execute`
- `log`

## Source
Lines 4–79 in `ruby/complex/services/report_service.rb`

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
| calls | [find](/ruby/complex/services/report_service/find.md) |
| calls | [due?](/ruby/complex/models/report/due.md) |
| calls | [execute](/ruby/complex/services/report_service/execute.md) |
| calls | [mark_as_run!](/ruby/complex/models/report/mark_as_run.md) |
