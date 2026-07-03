---
description: Execute all due scheduled reports.
resource: ruby/complex/services/report_service.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-02T18:44:20Z'
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

## Related

- [report_service](/ruby/complex/services/report_service.md)

## Calls

- [due?](/ruby/complex/models/report/due.md)
- [execute](/ruby/complex/services/report_service/execute.md)
- [mark_as_run!](/ruby/complex/models/report/mark_as_run.md)
