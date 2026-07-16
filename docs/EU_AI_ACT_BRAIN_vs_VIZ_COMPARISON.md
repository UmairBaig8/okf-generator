# EU AI Act Brain vs OKF Generator viz.html — Comparison Report

## 1. High-Level Architecture

| Aspect | EU AI Act Brain | OKF Generator viz.html |
|--------|----------------|----------------------|
| **Purpose** | Single-purpose knowledge graph for EU AI Act (68 concepts) | General-purpose OKF bundle browser + graph explorer |
| **Pages** | Single HTML page + `theme.js` (25 lines) | Single HTML page with all CSS/JS inline |
| **Graph Engine** | **Pure vanilla Canvas 2D** (no libraries) | **Cytoscape.js** (browse tab) + **custom Canvas** (explore tab) |
| **Extra libraries** | None for visualization | Cytoscape.js, marked.js, Prism.js, web-tree-sitter |
| **Lines of JS** | ~200 lines (graph) | ~2,100 lines (full app) |
| **Data** | Inline JSON (68 nodes, ~80 edges) | Inline JSON or dynamic `/api/*` endpoints |

## 2. Graph Rendering

| Feature | EU AI Act Brain | OKF Generator viz.html (Explore tab) |
|---------|----------------|--------------------------------------|
| **Canvas** | Single `<canvas id="c">` | `<div id="cosmos-container">` with child canvas |
| **Retina** | Yes, `devicePixelRatio` scaling via `setTransform` | Implemented similarly |
| **Node shape** | Circles (`arc`), radius = `6 + sqrt(deg)*2.2` | Circles (radius proportional to degree) |
| **Node colors** | 4 semantic types: concept (#4f9dff), fact (#f0a04b), entity (#a371f7), process (#3fb950) | 12+ code types: Class, Function, Module, Dependency, etc. |
| **Edge style** | Straight lines, arrowheads on hovered edges, edge labels with bg rect | Straight lines, arrowheads, edge labels |
| **Labels** | AABB collision avoidance, sorted by (focus > degree) | Similar collision-avoidance label placement |
| **Clusters** | No clustering | **Cluster labels** layer (e.g. "bundle", "namespace" grouping) |
| **Animation** | `requestAnimationFrame` loop | `requestAnimationFrame` loop |

## 3. Layout / Physics

| Feature | EU AI Act Brain | OKF Generator viz.html (Explore tab) |
|---------|----------------|--------------------------------------|
| **Algorithm** | Custom O(n²) Coulomb + Hooke | Custom O(n²) force-directed (similar approach) |
| **Alpha decay** | `alpha *= 0.985`, stops at 0.005 | Implemented (configurable) |
| **Repulsion** | `2600 / d²` | Similar inverse-square |
| **Springs** | Rest length 90px, stiffness 0.04 | Configurable rest length/stiffness |
| **Centering** | `-n.x * 0.002 * alpha` | Implemented |
| **Damping** | `vx *= 0.86` per tick | Implemented |
| **Initial layout** | Circle of radius 300 | Circle or random |
| **Modes** | Single explore mode | **4 modes**: Explore, Paths, Labels, Focus |

## 4. Interaction Model

| Feature | EU AI Act Brain | OKF Generator viz.html |
|---------|----------------|----------------------|
| **Hover** | Highlights node + immediate neighbors, fades rest | Highlights node + neighbors, shows tooltip (`#hover-tag`) |
| **Click** | Opens side detail panel (#panel) with type/title/summary/tags/related | Opens floating info card (`#cosmos-info-card`) with calls/called-by/related stats |
| **Drag node** | Yes, boosts alpha for re-settling | Yes |
| **Pan canvas** | Yes (mousedown on empty space + `view.x/y`) | Yes |
| **Zoom** | Scroll wheel, clamp [0.15, 4], centered on mouse | Scroll wheel + zoom buttons (`#zoomctl`) |
| **Search** | Input highlights matching nodes, dims rest | Input highlights + filters; also has type filter chips (`#chip-row`) |
| **Theme chips** | 9 theme-filter chips (Roles, High-risk, GPAI, Governance, etc.) | Filter chips built dynamically from bundle data |
| **Legend** | Toggle by type (concept/fact/entity/process) with counts | Toggle by type with counts, collapsible |
| **Deep linking** | `#node=<id>` hash, auto-select on load | `#node=<id>` hash support |
| **Reset view** | "Reset view" button, resets center + alpha | "Fit to screen" button + zoom controls |
| **Physics pause** | Not exposed in UI | Dedicated pause/resume physics button |
| **Show details** | Side panel slides in | Floating card + "Show Details" button switches to Browse tab |

## 5. Browse Tab (Tree + Detail)

| Feature | EU AI Act Brain | OKF Generator viz.html |
|---------|----------------|----------------------|
| **Browse** | Concept index grid (cards below graph) | **Full sidebar tree** with folder hierarchy, breadcrumbs, landing page with stats |
| **Tree** | Flat card grid | Hierarchical folder tree with collapse/expand |
| **Filters** | Theme chips only | **3 dropdown filters**: Bundle, Type, Language |
| **Detail view** | Right-side panel with type/title/summary/tags/related | Full right-pane with **2 sub-tabs**: Details + Code |
| **Code view** | Not present | Syntax-highlighted code (Prism.js) + **tree-sitter parse tree** |
| **Ego graph** | Not present | Cytoscape ego graph in detail sidebar |
| **Markdown** | Plain text | Full markdown rendering (marked.js) |
| **Relationships** | Related links with verb labels | Calls / Called-by / Related stats |
| **Breadcrumbs** | Not present | Hierarchical breadcrumb with navigation |

## 6. Visual Design

| Aspect | EU AI Act Brain | OKF Generator viz.html |
|--------|----------------|----------------------|
| **Font** | Playfair Display (headings) + DM Sans (body) | Inter (body) + JetBrains Mono (code) |
| **Color palette** | 5 semantic CSS vars + 4 type colors | 12 type colors + accent purple, extensive token system |
| **Glassmorphism** | Minimal (nav blur only) | Heavy — all panels have `backdrop-filter: blur(24px)`, frosted glass effect |
| **Dark theme** | `--bg: #0a0e1a`, `--panel: #111827` | `--bg: #0a0a0f`, `--surface: #131319` |
| **Light theme** | Toggle via `.light` class on `<body>` | Toggle via `html[data-theme="light"]` |
| **Background** | Solid colors | **Ambient background images** (bg-dark.png / bg-light.png) |
| **Custom scrollbar** | No | Yes (styled webkit scrollbar matching theme) |
| **Animations** | Minimal | `fadeIn` transitions, smooth hover effects |
| **Responsive** | Basic (mobile-friendly layout) | Similar responsive breakpoints |

## 7. Data Handling

| Feature | EU AI Act Brain | OKF Generator viz.html |
|---------|----------------|----------------------|
| **Data mode** | Static only (inline JSON) | **Dual mode**: Static (inline JSON) or Dynamic (`/api/*` REST endpoints) |
| **Concept info** | Pre-processed per node | Either pre-processed or fetched via `/api/concept/:id` |
| **Search** | Client-side filter on title/id/tags | Same approach, client-side token matching |
| **Graph data** | Inline `DATA.nodes` + `DATA.edges` | From `BUNDLE_DATA` object or `/api/graph` |

## 8. What Each Does Better

### EU AI Act Brain strengths:
- **Full-page dedicated graph** — the graph IS the page, no secondary navigation
- **Cleaner UX** — single focused purpose, no mode switching
- **Relationship labels on edges** — "defines", "triggers", "comprises" visible on hover
- **Edge arrowheads** — directional flow shown with triangle arrows
- **Theme-based filtering** — 9 curated themes matching AI Act domains
- **Smooter initial experience** — graph loads immediately, no tab switching
- **Self-contained** — zero external deps for graph, ~200 lines of JS total

### OKF Generator viz.html strengths:
- **Much richer interaction** — 4 explore modes, physics pause, zoom buttons
- **Browse tab with tree navigation** — hierarchical exploration of large bundles
- **Code + parse tree view** — shows actual source code and AST
- **Ego graph** — per-concept mini-graph in detail view
- **Detail panel** — full markdown rendering, syntax highlighting
- **Dual mode** — works both statically and server-backed
- **Cluster labels** — namespace grouping in explore view
- **Filter system** — by type, language, bundle (not just theme)
- **Token system** — extensive CSS custom properties for easy theming
- **Frosted glass UI** — polished glassmorphism aesthetics
- **Scalable** — handles 1000+ concepts (the other handles 68)

## 9. Key Missing Features

| Feature Missing from EU AI Act Brain | Feature Missing from OKF viz.html |
|--------------------------------------|-----------------------------------|
| No code/source view | No edge relationship labels visible during normal explore |
| No hierarchical tree | No theme-based chips (only type/lang/bundle filters) |
| No ego graph | Graph not visible by default (hidden behind Explore tab) |
| No physics controls | Concept index not shown in-page below graph |
| No mode switching | No edge arrowheads in explore mode |
| ~68 node limit (data is hardcoded) | Heavy ~2,100 lines of JS vs 200 |

## 10. Recommendations for viz.html

If you want to incorporate EU AI Act Brain's best features:

1. **Edge relationship labels + arrowheads** — their edge label rendering (bg rect + centered text + arrowhead triangle on hover) is excellent. Port the approach to the cosmos `drawEdge()` function.

2. **Theme chips** — their pre-defined theme concept is domain-specific, but the chip UI pattern could replace or augment the type/language filter chips for curated graph views.

3. **Dedicated graph-first experience** — consider making the Explore tab the default view (it currently requires clicking a tab). The EU page puts the graph front and center.

4. **Always-visible hover highlight** — their hover dims non-adjacent nodes to `alpha=0.15` while keeping neighbors full-brightness. The cosmos view partially does this but could match the smoothness.

5. **Collision-avoidance label priority** — their label sorting by `(focus?1:0, degree)` then AABB check is a nice lightweight approach vs. a full quadtree or force-based label layout.
