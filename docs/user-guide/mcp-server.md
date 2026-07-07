# MCP Server

`okf mcp` starts a Model Context Protocol server over your bundle, exposing 11 tools that let any MCP-compatible agent (Claude Desktop, Claude Code, or any MCP client) query your codebase's knowledge graph directly — no manual `okf lookup` calls, no copy-pasting output into chat.

## Starting the Server

```bash
okf mcp ./okf_bundle
```

By default this runs over stdio, which is what most MCP clients (Claude Desktop, Claude Code) expect for local servers.

## Registering with Claude Desktop / Claude Code

Add to your MCP client config (e.g. `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "okf-generator": {
      "command": "okf",
      "args": ["mcp", "/absolute/path/to/okf_bundle"]
    }
  }
}
```

Or, if you've already run `okf install claude`, this registration is handled for you automatically.

## Tools Exposed

| Tool | Purpose | Key Args |
|---|---|---|---|
| `lookup` | Exact-match concept search by name | `query: str`, `type?: str` |
| `get_concept` | Fetch full concept card by exact title | `title: str` |
| `find_callers` | Reverse call-graph — who calls this function | `concept_id: str` |
| `find_callees` | Forward call-graph — what does this function call | `concept_id: str` |
| `list_by_file` | All concepts extracted from a given source file | `file: str` |
| `list_dependencies` | All dependency concepts, optionally filtered by ecosystem | `ecosystem?: str` |
| `bundle_info` | Bundle-level metadata: concept counts, languages | none |
| `list_by_type` | All concepts of a given type | `type: str` |
| `search_by_tag` | Filter concepts by tag prefix (`lang:python`, `ecosystem:pip`) | `tag: str` |
| `get_related` | Related/referenced concepts for a given concept_id | `concept_id: str` |
| `get_manifest_source` | Manifest file info for a dependency | `concept_id: str` |

### `lookup`

Same semantics as `okf lookup` on the CLI — exact symbol match, not fuzzy/semantic.

```json
{ "query": "WorldBankConnector", "type": "class" }
```

Returns the full concept card: signature, docstring, params, methods, calls/called-by.

### `get_concept`

Use when you already know the exact `concept_id` (e.g. from a previous `lookup` or `find_callers` result) and want the full card without re-searching.

```json
{ "concept_id": "services/WorldBankConnector" }
```

### `find_callers`

Reverse edge traversal — returns everything in the bundle that calls the given concept. Useful before refactoring a function to see blast radius.

```json
{ "concept_id": "services/fetch_series" }
```

Returns entries from that concept's `Called By` section (see [Bundle Format Reference](bundle-format.md#call-graph-edges)), plus anything flagged under `Possible Calls` if resolution was ambiguous.

### `list_by_file`

```json
{ "path": "src/economic_data.py" }
```

Returns every concept — classes, functions, methods, constants — extracted from that one file. Good for "give me a map of this file" without dumping full source.

### `list_dependencies`

```json
{ "ecosystem": "pip" }
```

Omit `ecosystem` to list all dependencies across every manifest format found.

### `bundle_info`

No args. Returns:

```json
{
  "concept_count": 1842,
  "languages": ["python", "javascript", "sql"],
  "generated_at": "2026-07-01T10:22:03Z",
  "bundle_path": "./okf_bundle"
}
```

Useful for an agent to sanity-check it's talking to a fresh bundle before relying on it.

### `list_by_type`

```json
{ "type": "class" }
```

Valid `type` values match the [Concept Types](bundle-format.md#concept-types) table: `module`, `class`, `function`, `method`, `dependency`, `constant`, `interface`.

### `find_callees`

Forward edge traversal — returns everything in the bundle that the given concept references (calls, imports, or links to). Opposite of `find_callers`.

```json
{ "concept_id": "services/fetch_series" }
```

Useful when understanding a function's dependencies before refactoring.

### `search_by_tag`

List all concepts matching a tag prefix. Tags are key:value pairs stored on each concept during generation.

```json
{ "tag": "ecosystem:cargo" }
{ "tag": "lang:python" }
{ "tag": "domain:api" }
```

Common tag prefixes: `lang:`, `ecosystem:`, `domain:`, `module:`, `manifest:`, `git:branch:`, `git:repo:`.

### `get_related`

Returns structured related-concept links for a given concept_id. Includes both `related` (static call-graph links resolved during generation) and `related_semantic` (LLM-enriched cross-links, present only if `--enrich` was used).

```json
{ "concept_id": "cli" }
```

Response shape:

```json
{
  "related": [{ "title": "main", "concept_id": "cli/main" }],
  "related_semantic": []
}
```

### `get_manifest_source`

For a dependency concept, returns which manifest file declared it.

```json
{ "concept_id": "_dependencies/pip/requests" }
```

Response:

```json
{
  "concept_id": "_dependencies/pip/requests",
  "title": "requests",
  "manifest_file": "requirements.txt",
  "source_file": "src/requirements.txt",
  "ecosystem": "pip"
}
```

Only works for `Dependency`-type concepts.

## Why MCP Instead of Just Reading the Bundle Files

An agent *could* just `cat` bundle markdown files directly — bundles are plain files after all. MCP tools exist because:

- Exact-match `lookup` avoids the agent guessing file paths.
- `find_callers` / `find_callees` do graph traversal the agent would otherwise have to do manually across many files.
- Structured JSON responses are cheaper to parse than markdown scraping.
- Works identically whether the bundle is local or the agent connects over a remote MCP transport.

## Troubleshooting

See the [Troubleshooting](../troubleshooting.md) page for install and connection issues. Most MCP-specific problems come down to either a stale bundle (regenerate with `okf generate`) or an incorrect absolute path in the client config.