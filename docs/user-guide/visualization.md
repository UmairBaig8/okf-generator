# Visualization

okf-generator provides two ways to browse your knowledge bundle visually.

## Static HTML (no server required)

```bash
okf visualize ./okf_bundle
```

Generates a self-contained HTML file with:

- Force-directed graph of concepts and their relationships
- Search and filter by type
- Dark/light theme toggle
- Source code view for each concept
- Multi-bundle selector for monorepos

Output: `viz.html` in the bundle directory (or specify a path).

## Live dashboard (FastAPI)

```bash
# Install the dashboard extra
pip install "okf-generator[dashboard]"

# Launch
okf dashboard ./okf_bundle --open
```

The dashboard provides:

| Feature | Detail |
|---------|--------|
| **Search** | Full-text search with type, language, and tag filters |
| **Detail view** | Signature, params, docstring, source, tags, related links |
| **Interactive graph** | vis-network graph per concept showing related and used_by edges |
| **REST API** | Programmatic access at `/api/` endpoints |
| **Source tab** | Raw concept file content |

### API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/info` | Bundle statistics |
| `GET /api/types` | Concept type breakdown |
| `GET /api/languages` | Language breakdown |
| `GET /api/search?q=&type=&tag=&limit=` | Search concepts |
| `GET /api/concept/{concept_id}` | Full concept detail |
| `GET /api/graph?max_nodes=` | Graph data for visualization |
