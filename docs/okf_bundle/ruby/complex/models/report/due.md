---
concept_id: ruby/complex/models/report/due
language: ruby
okf_version: '0.2'
resource: ruby/complex/models/report.rb
tags:
- lang:ruby
- type:Function
- module:ruby
- domain:complex
- git:branch:HEAD
- git:repo:okf-generator
timestamp: '2026-07-07T06:58:41Z'
title: due?
type: Function
---

# due?

## Signature

```ruby
def due?()
```

## Source
Lines 56–64 in `ruby/complex/models/report.rb`

```rb
    def due?
      return true if @last_run.nil?
      interval_seconds = case @schedule
                         when "daily" then 86_400
                         when "hourly" then 3_600
                         else 0
                         end
      (Time.now.utc - @last_run) >= interval_seconds
    end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
| called_by | [ReportService](/ruby/complex/services/report_service/ReportService.md) |
| called_by | [Services](/ruby/complex/services/report_service/Services.md) |
| called_by | [run_due](/ruby/complex/services/report_service/run_due.md) |
