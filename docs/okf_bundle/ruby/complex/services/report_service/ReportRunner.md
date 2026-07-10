---
concept_id: ruby/complex/services/report_service/ReportRunner
description: Internal runner that executes report generation logic.
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
timestamp: '2026-07-10T14:57:28Z'
title: ReportRunner
type: Class
---

# ReportRunner

Internal runner that executes report generation logic.

## Signature

```ruby
class ReportRunner
```

## Docstring

Internal runner that executes report generation logic.

## Methods

- `initialize`
- `execute`
- `log`

## Source
Lines 64–78 in `ruby/complex/services/report_service.rb`

```rb
  class ReportRunner
    def initialize(report)
      @report = report
    end

    def execute
      @report.data = { generated: Time.now.utc.iso8601, status: "completed" }
    end

    protected

    def log(message)
      puts "[ReportRunner] #{message}"
    end
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report_service](/ruby/complex/services/report_service.md) |
