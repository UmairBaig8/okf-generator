---
concept_id: typescript/complex/services/user-service/Route
description: Route decorator stub for controller methods.
language: typescript
okf_version: '0.2'
resource: typescript/complex/services/user-service.ts
tags:
- lang:typescript
- type:Function
- module:typescript
- domain:complex
- git:branch:main
- git:repo:okf-generator
timestamp: '2026-07-10T15:03:07Z'
title: Route
type: Function
---

# Route

Route decorator stub for controller methods.

## Signature

```typescript
function Route(method: string, path: string): (target: unknown, propertyKey: string, descriptor: PropertyDescriptor) => void
```

## Docstring

Route decorator stub for controller methods.

## Source
Lines 34–38 in `typescript/complex/services/user-service.ts`

```ts
function Route(method: string, path: string): (target: unknown, propertyKey: string, descriptor: PropertyDescriptor) => void {
  return (target: unknown, propertyKey: string, descriptor: PropertyDescriptor): void => {
    Reflect.defineMetadata('route', { method, path }, descriptor.value);
  };
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user-service](/typescript/complex/services/user-service.md) |
| called_by | [UserService](/typescript/complex/services/user-service/UserService.md) |
