---
concept_id: typescript/complex/services/user-service/Logged
description: Decorator that logs method invocations to the console.
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
timestamp: '2026-07-10T14:55:12Z'
title: Logged
type: Function
---

# Logged

Decorator that logs method invocations to the console.

## Signature

```typescript
function Logged(target: unknown, propertyKey: string, descriptor: PropertyDescriptor): void
```

## Docstring

Decorator that logs method invocations to the console.

## Source
Lines 14–20 in `typescript/complex/services/user-service.ts`

```ts
function Logged(target: unknown, propertyKey: string, descriptor: PropertyDescriptor): void {
  const original = descriptor.value;
  descriptor.value = function (...args: unknown[]) {
    console.log(`[UserService] ${propertyKey} called with`, args);
    return original.apply(this, args);
  };
}
```

## Relationships

| Type | Target |
|------|--------|
| related | [user-service](/typescript/complex/services/user-service.md) |
