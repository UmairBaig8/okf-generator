---
concept_id: csharp/complex/Repositories/IOrderRepo/IRepository
language: csharp
okf_version: '0.2'
resource: csharp/complex/Repositories/IOrderRepo.cs
tags:
- lang:csharp
- type:Interface
- module:csharp
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T14:55:11Z'
title: IRepository
type: Interface
---

# IRepository

## Signature

```csharp
interface IRepository
```

## Methods

- `Save`
- `FindById`
- `FindAll`
- `Delete`
- `Count`

## Source
Lines 9–16 in `csharp/complex/Repositories/IOrderRepo.cs`

```cs
public interface IRepository<T>
{
    T Save(T entity);
    T? FindById(string id);
    IReadOnlyList<T> FindAll();
    bool Delete(string id);
    long Count();
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [IOrderRepo](/csharp/complex/Repositories/IOrderRepo.md) |
