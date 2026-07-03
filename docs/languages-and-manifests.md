# Language & Manifest Coverage

## Code Languages

| Language | Parser | Extracts |
|---|---|---|
| Python | stdlib `ast` | Functions, classes, params, return types, docstrings |
| JavaScript / TypeScript | tree-sitter | Functions, arrow fns, classes, JSDoc |
| Go | tree-sitter | Funcs, methods, structs, interfaces, GoDoc |
| Java | tree-sitter | Classes, methods, constructors, Javadoc |
| Rust | tree-sitter | Fns, structs, enums, traits, impl blocks, `///` |
| **Swift** | tree-sitter | Classes, structs, enums, protocols, generics, methods, properties, doc comments |
| **Kotlin** | tree-sitter | Classes, data classes, objects, enums, interfaces, generics, functions, constructor params |
| Ruby | tree-sitter | Defs, classes, modules, `#` comments |
| C | tree-sitter | Functions, structs with `/**` doc comments |
| C++ | tree-sitter | Functions, classes, structs, methods with `///` doc comments |
| C# | tree-sitter | Classes, methods, top-level functions |
| SQL | tree-sitter | Tables, views, functions, indexes, types, triggers with preceding `--`/`/* */` comments |

## Manifest / Build Files

| Format | Parser | Extracts |
|---|---|---|
| `requirements.txt` | regex | pip package names + version constraints |
| `pyproject.toml` | `tomllib` | PEP 621 deps + optional-dependencies + Poetry legacy |
| `package.json` | `json` | npm/Node dependencies + devDependencies |
| `Cargo.toml` | `tomllib` | Rust crate deps + dev/build-dependencies |
| `Cargo.lock` | `tomllib` | Rust lockfile — pinned versions from `[[package]]` entries |
| `yarn.lock` | regex | Yarn lockfile (v1) — package name + pinned versions |
| `pnpm-lock.yaml` | `yaml` | pnpm lockfile — package name + version + dev flag |
| `go.mod` | regex | Go module deps + `// indirect` flag |
| `go.sum` | regex | Go checksum lockfile — deduplicated module versions |
| `poetry.lock` | `tomllib` | Python Poetry lockfile — `[[package]]` with dev category detection |
| `composer.json` | `json` | PHP packages (skips `php`/`ext-*` platform entries) |
| `pom.xml` | `xml.etree.ElementTree` | Maven dependencies + `test`/`provided` scope => dev |
| `Gemfile` | regex | Ruby gems + `group :test/:development` => dev |
| `build.gradle` / `.kts` | regex | Gradle deps (Groovy + Kotlin DSL) + `testImplementation` => dev |
| `Package.swift` | regex | SwiftPM packages from `.package(url:from:)` |
| `project.clj` | regex | Clojars deps + `:dev` profile |
| `mix.exs` | regex | Hex packages + `only: :dev/:test` => dev |

## Architectural Query Examples

The dependency cross-referencing across all 17 formats enables queries that would otherwise require grepping multiple build systems:

### Find every microservice depending on a deprecated Rust crate

```bash
# List all Rust dependencies across the entire monorepo
okf lookup --type Dependency --tag ecosystem:cargo --compact

# Check if any service pins an outdated version
okf lookup --type Dependency openssl
```

### Track a vulnerable Python package across all services

```bash
# Find all pip dependencies named "requests"
okf lookup --type Dependency --tag ecosystem:pip requests

# See which modules depend on it
okf lookup --type Dependency requests --json | jq '.[].called_by'
```

### Audit npm transitive dependencies

```bash
# All npm packages across every service
okf lookup --type Dependency --tag ecosystem:npm --compact

# Filter by version constraint
okf lookup --type Dependency --tag ecosystem:npm express
```

### Cross-ecosystem queries

The bundle indexes all ecosystems into a unified format, so you can ask questions across language boundaries:

```bash
# All external dependencies, grouped by ecosystem
okf lookup --type Dependency --compact

# Which dev dependencies are we using across all projects?
okf lookup --type Dependency --tag dev:true --compact
```

### CI/CD integration

Automate these queries in your CI pipeline:

```bash
# Fail the build if any dependency is deprecated
okf lookup --type Dependency --tag deprecated:true --compact
if [ $? -eq 0 ]; then echo "Deprecated deps found!"; exit 1; fi
```
