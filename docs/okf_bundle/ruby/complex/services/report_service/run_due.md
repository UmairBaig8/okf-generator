---
concept_id: ruby/complex/services/report_service/run_due
description: Execute all due scheduled reports.
language: ruby
okf_version: '0.2'
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-11T09:38:55Z'
title: run_due
type: Function
---

# run_due

Execute all due scheduled reports.

## Signature

```ruby
def run_due()
```

## Docstring

Execute all due scheduled reports.
@yield [Models::ScheduledReport] each report that was executed
@return [Array<Models::ScheduledReport>] executed reports

## Returns
`Array<Models::ScheduledReport>`

## Source
Lines 41–49 in `ruby/complex/services/report_service.rb`

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
| calls | [due?](/ruby/complex/models/report/due.md) |
| calls | [execute](/ruby/complex/services/report_service/execute.md) |
| calls | [mark_as_run!](/ruby/complex/models/report/mark_as_run.md) |
