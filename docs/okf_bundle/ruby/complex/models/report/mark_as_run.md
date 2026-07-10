---
concept_id: ruby/complex/models/report/mark_as_run
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
title: mark_as_run!
type: Function
---

# mark_as_run!

## Signature

```ruby
def mark_as_run!()
```

## Source
Lines 52–54 in `ruby/complex/models/report.rb`

```rb
    def mark_as_run!
      @last_run = Time.now.utc
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
| called_by | [ReportService](/ruby/complex/services/report_service/ReportService.md) |
| called_by | [Services](/ruby/complex/services/report_service/Services.md) |
| called_by | [run_due](/ruby/complex/services/report_service/run_due.md) |
