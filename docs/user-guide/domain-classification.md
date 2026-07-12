# Domain Classification

Domain classification re-classifies YAML-sourced concepts using data-driven rule files. No code changes needed for new domains — just add a `.yaml` rule file.

**Use cases:**
- Crossplane (XRD, Composition V1/V2, Claim, ProviderConfig)
- Helm charts (HelmRelease, HelmChartConfig)
- Kubernetes native resources (Deployments, Services, ConfigMaps)
- Any YAML-based domain with known schemas

---

## Quick Start

```bash
# List available built-in domains
okf domains

# Generate with Crossplane domain classification
okf generate ./src ./bundle --domains crossplane

# Generate with a custom rule file
okf generate ./src ./bundle --domain-rules ./my-rules.yaml

# Combine built-in + custom
okf generate ./src ./bundle --domains crossplane --domain-rules ./my-overrides.yaml

# Validate your rule file before using it
okf domains validate ./my-rules.yaml
```

---

## How It Works — Three Steps

```
YAML files (.yaml/.yml)
    │
    ▼
[1] YAML Parser (Layer 1)
    ├── Parses with yaml.safe_load_all()  (multi-doc --- support)
    ├── Produces per file: 1 Module + N Resource concepts
    │   (Module = file-level wrapper, never reclassified)
    │   (Resource = one per YAML document — carries body_extra.yaml_doc)
    └── Stores raw parsed dict on Resource concepts only
    │
    ▼
[2] Domain Engine (Layer 3) runs AFTER scan_codebase()
    ├── Loads rule files (built-in + project + CLI)
    ├── Matches each **Resource** concept's yaml_doc against rule conditions
    ├── Re-classifies type, adds tags, extracts fields
    │   (Module concepts are invisible to domain rules — they stay as-is)
    └── Links cross-references (Composition→XRD, Claim→XRD)
    │
    ▼
[3] Audit log shows what matched
    Domain classification audit: 12 concepts matched, 1 unmatched
      Rule [XRD] matched 1 concept(s)
      Rule [Composition-V2-Pipeline] matched 2 concept(s)
      Rule [Composition-V1-Style] matched 1 concept(s)
      Rule [ManagedResource] matched 5 concept(s)
```

---

## Rule File Format — Full Reference

A rule file is a single YAML document with a `domain` name and a list of `rules`.

```yaml
domain: my-domain               # Required: domain name (used for merging)
rules:                          # Required: list of classification rules

  - name: MyRuleName            # Optional: used in audit logs
    match:                      # Required: conditions to match a concept
      kind: "MyKind"            #   Exact string match
      apiVersion: {"$glob": "example.io/*"}  # Glob match

    type: MyType                # New concept type if matched
    add_tags:                   # Tags to add
      - domain:my-domain
      - my-tag

    extract:                    # Extract YAML fields into concept fields
      - from: spec.group        #   Dot-path to extract from yaml_doc
        to: returns             #   Destination concept field
      - from: spec.names.kind
        to: signature
      - from: spec.versions[0].schema.properties
        to: fields
      - from: spec.pipeline[*].functionRef.name
        to: fields

    links:                      # Cross-reference links to other concepts
      - field: spec.compositeTypeRef     # Field to extract from yaml_doc
        target_type: XRD                 # Target concept type to link to
        match_on: [apiVersion, kind]     # Fields to match against target
```

---

## Match Conditions — Complete Reference

### 1. Exact String Match

```yaml
match:
  kind: "Composition"           # Must equal "Composition"
  apiVersion: "v1"              # Must equal "v1"
```

### 2. Glob Match (`$glob`)

```yaml
match:
  apiVersion: {"$glob": "apiextensions.crossplane.io/*"}   # Wildcard prefix
```

Matches any value that fits the glob pattern. Uses standard `fnmatch` syntax — `*` matches any sequence, `?` matches single character.

Common patterns:
```yaml
{"$glob": "apiextensions.crossplane.io/*"}   # Any version of crossplane apiextensions
{"$glob": "*.crossplane.io/*"}               # Any crossplane API group
{"$glob": "pkg.crossplane.io/*"}             # Crossplane packages only
```

### 3. Regex Match (`$regex`)

```yaml
match:
  kind: {"$regex": "^X.*"}      # Starts with "X" (XRD claim names)
  metadata.name: {"$regex": "prod-"}   # Contains "prod-"
```

Uses Python's `re.search()` — matches if the pattern is found **anywhere** in the value. Use `^` for start-anchored, `$` for end-anchored. Standard Python regex syntax applies (no custom dialect).

### 4. Presence Check (`has_key`)

```yaml
match:
  has_key: "spec.resources"     # The doc MUST have this key
```

Useful when a value-based match won't work — e.g., detecting V1-style Compositions that lack `spec.mode` but have `spec.resources`:

```yaml
# V1 Composition: has spec.resources but no spec.mode
- match:
    kind: "Composition"
    has_key: "spec.resources"

# V2 Pipeline Composition: has spec.mode: Pipeline
- match:
    kind: "Composition"
    spec.mode: "Pipeline"
```

Also accepts a list to require multiple keys:
```yaml
match:
  has_key: ["spec.resources", "spec.compositeTypeRef"]
```

### 5. Catch-all (`default`) with Guard (`require_keys`)

```yaml
match:
  default: true
  require_keys: [apiVersion, kind]   # Only match k8s-like resources
```

The catch-all rule is evaluated last (all other rules are tried first). The `require_keys` guard prevents it from matching non-k8s YAML like CI configs, Helm values, or settings files.

### 6. Multiple Conditions (AND)

Multiple keys in the same `match:` block are ANDed — all must match:

```yaml
match:
  apiVersion: {"$glob": "apiextensions.crossplane.io/*"}
  kind: "Composition"
  has_key: "spec.resources"
  spec.compositeTypeRef.kind: "X*"    # Regex not shown but would work
```

### Match Priority Rules

1. **First-match-wins** within a rule file — earlier rules take priority
2. **Catch-all (`default: true`) is always evaluated last** within that domain
3. **Multi-domain ordering** — `--domains A,B` evaluates A's rules first, then B

---

## Extract Paths — Dot-Path Reference

The `from` field in extract rules uses dot-path notation to navigate the YAML document:

| Path | Description | Example Value |
|------|-------------|---------------|
| `spec.group` | Simple nested key | `"example.org"` |
| `spec.names.kind` | Deeper nesting | `"XPostgreSQLInstance"` |
| `spec.versions[0].name` | List index (0-based) | `"v1alpha1"` |
| `spec.versions[*].name` | Wildcard (first item) | `"v1alpha1"` |
| `spec.pipeline[*].functionRef.name` | Wildcard through list + nested | `"function-kro"` |
| `metadata.name` | Top-level common field | `"my-db"` |

### Destination Fields (`to`)

| `to` value | Concept field | Accepts |
|-----------|--------------|---------|
| `signature` | `Concept.signature` | string |
| `returns` | `Concept.returns` | string |
| `description` | `Concept.description` | string |
| `fields` | `Concept.fields` | dict (OpenAPI properties), string, or list of strings |

**`to: fields` accepts:**
- **dict** (e.g., OpenAPI `properties` object): **Replaces** the current `fields` list → each key becomes `{"name": k, "type": v.type, "visibility": ""}`
- **string** (e.g., a function name): **Appends** to the current `fields` list → `{"name": "function-kro", "type": "string", "visibility": ""}`
- **list of strings**: Each string **appended** as a separate field entry

Default behavior: `to: fields` with a dict **overwrites** any fields the YAML parser may have already set (e.g., top-level keys like `apiVersion`, `kind`). String/list extracts **append** to existing fields. If you need both, use separate extract rules (one dict, one string) or extract to different destinations.

---

## Link Rules — Cross-Reference Reference

Links create `related` edges between concepts — the same mechanism used by the code linker for function calls and imports.

```yaml
links:
  - field: spec.compositeTypeRef    # Extract this field from the matched doc
    target_type: XRD               # Target concept type (informational)
    match_on: [apiVersion, kind]   # Fields to match against target concepts
```

### How linking works

1. **Extract**: The linker extracts the `field` value from the matched concept's `yaml_doc`
2. **Index**: All concepts are indexed by `concept_id` and key fields (name, kind, apiVersion)
3. **Match**: The extracted value is compared against the concept index. See "Match behavior" below for how multiple matches are handled
4. **Link**: All matching concept IDs are added to the source concept's `related` list

### Match behavior — multiple matches

Links resolve to **ALL** concepts that match the criteria, not just the first one.

**Dict-based links** (e.g., `spec.compositeTypeRef` → `{apiVersion, kind}`):
- The linker finds every concept where `body_extra.yaml_doc.apiVersion == X` AND `body_extra.yaml_doc.kind == Y`
- In a single-XRD repo, this resolves 1:1 (one Composition → one XRD)
- In a multi-XRD repo, this can resolve 1:N (one Composition → multiple XRDs of the same apiVersion/kind)

**Template-based links** (e.g., `spec.resources[*].base` → `{apiVersion, kind}`):
- The extracted value is a *template* describing what kind of ManagedResource to create
- The linker links to **all** existing ManagedResource concepts matching that apiVersion/kind pair
- If three `RDSInstance` manifests exist in the bundle, all three appear in `related`

This means `related` for a Composition may include:
- **Specific references**: The one XRD it actually composes (via `compositeTypeRef`)
- **Template matches**: All ManagedResources whose apiVersion/kind match its resource templates (via `resources[*].base`)

### Example: Composition → XRD (1:1 reference)

```yaml
# In a Composition concept's yaml_doc:
spec:
  compositeTypeRef:
    apiVersion: "example.org/v1"
    kind: "XPostgreSQLInstance"

# Link config:
links:
  - field: spec.compositeTypeRef
    target_type: XRD
    match_on: [apiVersion, kind]
```

The linker finds the XRD concept whose `body_extra.yaml_doc` has `apiVersion: "example.org/v1"` AND `kind: "XPostgreSQLInstance"`, then adds `xrd-concept-id` to the Composition's `related` list.

---

## V1 vs V2 Crossplane — Practical Example

The built-in crossplane rules distinguish between V1 (resources/patches) and V2 (pipeline/functions) Compositions.

### V1 Composition (patch/resources style)

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  compositeTypeRef:
    apiVersion: example.org/v1
    kind: XPostgreSQLInstance
  resources:                     # ← V1 indicator: has_key: spec.resources
    - name: rds-instance
      base:
        apiVersion: database.aws.crossplane.io/v1beta1
        kind: RDSInstance
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.storageGB
          toFieldPath: spec.forProvider.storageGB
```

→ Classified as `type: Composition` with tags: `crossplane-v1-style`

### V2 Composition (pipeline style)

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  mode: Pipeline                  # ← V2 indicator: spec.mode == "Pipeline"
  compositeTypeRef:
    apiVersion: example.org/v1
    kind: XPostgreSQLInstance
  pipeline:                       # functions pipeline
    - functionRef:
        name: function-kro        # ← extracted to fields
      step: validate
    - functionRef:
        name: function-auto-ready
      step: ready
```

→ Classified as `type: Composition` with tags: `crossplane-v2-pipeline`
→ Pipeline function names (`function-kro`, `function-auto-ready`) extracted to `fields`

---

## Audit Log — Verifying Your Rules

Every time domain classification runs, the engine logs a summary of what matched:

```
Domain classification audit: 12 concepts matched, 1 unmatched
  Rule [XRD] matched 1 concept(s)
  Rule [Composition-V2-Pipeline] matched 2 concept(s)
  Rule [Composition-V1-Style] matched 1 concept(s)
  Rule [Composition-Generic] matched 0 concept(s)
  Rule [ManagedResource] matched 5 concept(s)
  Rule [ProviderConfig] matched 1 concept(s)
```

**What to check:**
- **`0 unmatched`** means all YAML concepts were classified by some rule. If there are unmatched concepts, they stayed as the generic `Resource` type.
- **`Rule [X] matched 0 concept(s)`** means a rule never fired — check your match conditions. This is useful during rule authoring.
- **Rules with `0 matched` that SHOULD have matched** indicate incorrect match conditions or rule ordering (a higher-priority rule caught it first).

---

## Rule Validation

Use `okf domains validate` to check a rule file for structural errors before using it:

```bash
okf domains validate ./my-rules.yaml
```

Output for a valid file:
```
✅ ./my-rules.yaml — valid
```

Output for an invalid file:
```
❌ ./my-rules.yaml — 2 error(s):

   • rules[0]: missing 'match' block (required)
   • rules[0].extract[0]: 'to' must be one of {'returns', 'signature', 'fields', 'description'}
```

**What validation checks:**
| Check | Description |
|-------|-------------|
| File exists + readable | Checks path and parseable YAML/JSON |
| `domain` field | Must be a non-empty string |
| `rules` is a list | Must be present and a list |
| Each rule has `match` | Match block is required |
| Match operator validity | Only `$glob` and `$regex` are valid dict operators (not `$badop`) |
| Extract `from`/`to` | Both required; `to` must be a valid field name |
| Link `field`/`match_on` | Both required |
| Empty rules list | Warns if no rules defined |

---

## Writing Your Own Domain Rules — Step-by-Step

### Step 1: Identify the pattern

Look at the YAML files in your domain. What fields reliably identify the resource type?

For a hypothetical "HelmRelease" domain:
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmRelease
metadata:
  name: my-release
spec:
  chart:
    name: nginx
    version: "1.0.0"
```

Key identifiers: `apiVersion: helm.cattle.io/v1` and `kind: HelmRelease`.

### Step 2: Create the rule file

```yaml
domain: helm
rules:
  - name: HelmRelease
    match:
      apiVersion: {"$glob": "helm.cattle.io/*"}
      kind: "HelmRelease"
    type: HelmRelease
    add_tags:
      - domain:helm
      - helm-release
    extract:
      - from: spec.chart.name
        to: signature
      - from: spec.chart.version
        to: returns
```

### Step 3: Validate

```bash
okf domains validate ./helm-rules.yaml
```

### Step 4: Use it

```bash
okf generate ./src ./bundle --domain-rules ./helm-rules.yaml
```

### Step 5: Check the audit

Verify your rules fired correctly:
```
Domain classification audit: 5 concepts matched, 0 unmatched
  Rule [HelmRelease] matched 3 concept(s)
```

---

## Multi-Doc Files

YAML files can contain multiple documents separated by `---`. Each document is parsed independently by the YAML parser and becomes its own Resource concept with its own `body_extra.yaml_doc`. Domain rules match each document independently.

Example — a single file containing both a Composition and an XRD:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.example.org
spec:
  group: example.org
  names:
    kind: XPostgreSQLInstance
---
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xpostgresqlinstances.example.org
spec:
  compositeTypeRef:
    apiVersion: example.org/v1
    kind: XPostgreSQLInstance
  mode: Pipeline
  pipeline:
    - functionRef:
        name: function-kro
```

Running `--domains crossplane` against this file produces two matched concepts:

```
Domain classification audit: 2 concepts matched, 0 unmatched
  Rule [XRD] matched 1 concept(s)                     ← first document
  Rule [Composition-V2-Pipeline] matched 1 concept(s)  ← second document
```

Each document's type is set independently — one becomes `XRD`, the other `Composition`. The link between them (Composition → XRD via `compositeTypeRef`) is resolved in the linker pass.

---

## Multi-Domain Composition

When using `--domains A,B`, domains are evaluated in list order:

```bash
okf generate ./src ./bundle --domains crossplane,helm
```

- Domain A (`crossplane`) rules get first shot at every concept
- If no rule in A matches, the concept falls through to Domain B (`helm`)
- Within each domain, rules are first-match-wins, with catch-all last
- Domain A's catch-all fires before Domain B's first rule

This means **put more specific domains first** and **generic/catch-all domains last**.

---

## Project-Local Overrides

Place rule files in `.okf/domains/` for project-specific overrides (git-committable):

```
.okf/
└── domains/
    ├── crossplane.yaml     # Overrides built-in crossplane rules
    └── team-specific.yaml  # New domain, additive
```

Same `domain` key = user rules override built-in rules. New `domain` key = additive.

---

## Rule Sources — Priority Order (highest to lowest)

| Source | Path | Overrides |
|--------|------|-----------|
| CLI | `--domain-rules ./file.yaml` | Everything |
| Project | `.okf/domains/*.yaml` | Built-in (same domain key) |
| Built-in | `okf/domains/rules/*.yaml` | Base rules for known domains |

All rules with the same `domain` key are merged — project rules replace built-in rules with matching names. Rules with different `domain` keys are additive.

---

## Limitations

### Composition Functions — only function names, not pipeline logic

The `extract` rule for V2 Pipeline Compositions surfaces `spec.pipeline[*].functionRef.name` — so the AI agent sees **which** function is used (e.g., `function-kro`, `function-auto-ready`). What the function **does** internally (KCL logic, Go-template strings, embedded code in `spec.pipeline[*].in`) is **not** extracted. Dot-path extraction cannot reach into string-embedded configuration logic. Function names are visible; function behavior is not.

### Claim cross-linking requires prior XRD classification

A Claim references its XRD via `spec.compositeRef` (e.g., `apiVersion: example.org/v1, kind: XPostgreSQLInstance`). The linker resolves this by matching against already-classified XRD concepts in the same bundle. If the XRD and Claim are in separate repos or different `okf generate` runs, the link won't resolve. Cross-bundle linking is not supported — both the source and target must exist in the same generation pass.

### Template-based links are approximate

Links using `spec.resources[*].base` (Composition → ManagedResource templates) match by `apiVersion + kind` against all existing concepts. If a repo has no actual `RDSInstance` manifests (because the Composition creates them dynamically), the link resolves to zero concepts. This is correct behavior — the link describes a *template reference*, not an *instance reference* — but it may surprise users who expect "links" to always resolve to something solid.

### Regex dialect

The `$regex` operator uses Python's `re.search()` — **NOT** grep, PCRE, or JavaScript regex. Key differences:
- `^` and `$` anchor to start/end of string (same as most dialects)
- No lookbehind/lookahead support (Python `re` doesn't support variable-length lookbehind)
- `\d`, `\w`, `\s` shorthand classes work (same as most dialects)
- No `(?i)` inline case-insensitive flag — use `[Aa]` or pre‑normalize values

---

## Best Practices

1. **Name your rules** — `name:` field makes audit logs readable
2. **Test with a single file first** — `okf generate ./test-file.yaml /tmp/test --domains your-domain`
3. **Check the audit log** — verify your rules matched what you expected
4. **Validate before using** — `okf domains validate ./rules.yaml`
5. **Use `has_key` for structural detection** — more reliable than regex for "does this key exist"
6. **Catch-all should always have `require_keys`** — prevents misclassifying unrelated YAML
7. **Put specific rules before generic ones** — first-match-wins
8. **V1/V2 differentiation** — match on `spec.mode` for the new style, `has_key: spec.resources` for the legacy style
