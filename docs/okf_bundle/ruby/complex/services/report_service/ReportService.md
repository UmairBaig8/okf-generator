---
concept_id: ruby/complex/services/report_service/ReportService
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
timestamp: '2026-07-10T19:11:07Z'
title: ReportService
type: Class
---

# ReportService

## Signature

```ruby
class ReportService
```

## Methods

- `initialize`
- `generate`
- `schedule`
- `find`
- `run_due`
- `summary`
- `next_id`

## Source
Lines 5–61 in `ruby/complex/services/report_service.rb`

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
| calls | [find](/ruby/complex/services/report_service/find.md) |
| calls | [due?](/ruby/complex/models/report/due.md) |
| calls | [execute](/ruby/complex/services/report_service/execute.md) |
| calls | [mark_as_run!](/ruby/complex/models/report/mark_as_run.md) |
