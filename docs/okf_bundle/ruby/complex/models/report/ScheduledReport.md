---
concept_id: ruby/complex/models/report/ScheduledReport
description: A scheduled report that runs at a specific interval.
language: ruby
okf_version: '0.2'
resource: ruby/complex/models/report.rb
tags:
- lang:ruby
- type:Class
- module:ruby
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: ScheduledReport
type: Class
---

# ScheduledReport

A scheduled report that runs at a specific interval.

## Signature

```ruby
class ScheduledReport
```

## Inheritance

- `Report`

## Docstring

A scheduled report that runs at a specific interval.

## Methods

- `initialize`
- `mark_as_run!`
- `due?`

## Source
Lines 41–65 in `ruby/complex/models/report.rb`

```rb
  class ScheduledReport < Report
    include Exportable

    attr_reader :schedule, :last_run

    def initialize(id, title, schedule, data = {})
      super(id, title, data)
      @schedule = schedule
      @last_run = nil
    end

    def mark_as_run!
      @last_run = Time.now.utc
    end

    def due?
      return true if @last_run.nil?
      interval_seconds = case @schedule
                         when "daily" then 86_400
                         when "hourly" then 3_600
                         else 0
                         end
      (Time.now.utc - @last_run) >= interval_seconds
    end
  end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
