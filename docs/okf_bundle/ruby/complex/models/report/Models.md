---
concept_id: ruby/complex/models/report/Models
description: Domain model for generated reports.
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
timestamp: '2026-07-10T14:55:11Z'
title: Models
type: Class
---

# Models

Domain model for generated reports.

## Signature

```ruby
module Models
```

## Docstring

Domain model for generated reports.

## Methods

- `initialize`
- `to_h`
- `summary`
- `to_csv`
- `to_json`
- `initialize`
- `mark_as_run!`
- `due?`

## Source
Lines 2–66 in `ruby/complex/models/report.rb`

```rb
module Models
  class Report
    attr_reader :id, :title, :generated_at
    attr_accessor :data

    def initialize(id, title, data = {})
      @id = id
      @title = title
      @data = data
      @generated_at = Time.now.utc
    end

    def to_h
      {
        id: @id,
        title: @title,
        data: @data,
        generated_at: @generated_at.iso8601
      }
    end

    def summary
      "#{@title} (#{@data.length} entries)"
    end
  end

  # A report that can be exported to CSV format.
  module Exportable
    def to_csv
      @data.map { |row| row.values.join(",") }.join("\n")
    end

    def to_json
      require "json"
      to_h.to_json
    end
  end

  # A scheduled report that runs at a specific interval.
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
end
```

## Relationships

| Type | Target |
|------|--------|
| related | [report](/ruby/complex/models/report.md) |
| calls | [to_json](/ruby/complex/models/report/to_json.md) |
