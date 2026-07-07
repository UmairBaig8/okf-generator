# MCP Server

okf-generator includes a built-in Model Context Protocol (MCP) server, letting any MCP-compatible agent (Claude Desktop, Cursor, etc.) browse and search bundle concepts natively.

## Quick start

```bash
okf mcp ./okf_bundle
```

This starts the server in stdio mode — most MCP clients connect this way automatically.

For HTTP mode:

```bash
okf mcp ./okf_bundle --port 9000
```

## Available tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `lookup` | Search concepts by name, type, or tag | `query` (req), `type`, `tag`, `limit`, `detail` |
| `get_concept` | Full detail by concept_id | `concept_id` (req) |
| `find_callers` | Concepts that reference a given concept_id | `concept_id` (req) |
| `list_by_file` | All concepts from a source file | `file` (req) |
| `list_dependencies` | List dependencies, optionally filtered | `ecosystem` |
| `bundle_info` | Bundle statistics | none |
| `list_by_type` | All concepts of a specific type | `type` (req) |

## Example usage

```bash
# List all tools
echo '{"id":1,"method":"tools/list"}' | okf mcp ./okf_bundle

# Search for a concept
echo '{"id":1,"method":"tools/call","params":{"name":"lookup","arguments":{"query":"slugify"}}}' | okf mcp ./okf_bundle
```

## Claude Desktop setup

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "okf": {
      "command": "okf",
      "args": ["mcp", "/path/to/okf_bundle"]
    }
  }
}
```

## Protocol

The server implements MCP protocol version `2024-11-05` over stdio or HTTP+SSE. Resources are exposed under `okf://{concept_id}` URIs — one per concept.
