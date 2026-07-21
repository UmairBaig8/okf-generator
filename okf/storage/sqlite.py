"""SQLite-backed BundleStore — zero-dependency, embedded, fast."""
import json, os, re, sqlite3, time
from contextlib import contextmanager
from pathlib import Path

from okf.storage.base import BundleStore

SCHEMA_VERSION = 1

SQL_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS _meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS concepts (
    concept_id    TEXT PRIMARY KEY,
    type          TEXT NOT NULL,
    title         TEXT NOT NULL,
    description   TEXT DEFAULT '',
    resource      TEXT DEFAULT '',
    language      TEXT DEFAULT '',
    file_path     TEXT NOT NULL DEFAULT '',
    file_mtime    INTEGER DEFAULT 0,
    content_hash  TEXT DEFAULT '',
    sections_json TEXT DEFAULT '{}',
    timestamp     TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS concept_tags (
    concept_id TEXT NOT NULL REFERENCES concepts(concept_id),
    tag        TEXT NOT NULL,
    PRIMARY KEY (concept_id, tag)
);

CREATE TABLE IF NOT EXISTS edges (
    source  TEXT NOT NULL,
    target  TEXT NOT NULL,
    reltype TEXT NOT NULL,
    PRIMARY KEY (source, target, reltype)
);

CREATE INDEX IF NOT EXISTS idx_concepts_type     ON concepts(type);
CREATE INDEX IF NOT EXISTS idx_concepts_resource ON concepts(resource);
CREATE INDEX IF NOT EXISTS idx_concepts_language ON concepts(language);
CREATE INDEX IF NOT EXISTS idx_concepts_file     ON concepts(file_path);
CREATE INDEX IF NOT EXISTS idx_ct_tag            ON concept_tags(tag);
CREATE INDEX IF NOT EXISTS idx_edges_source      ON edges(source);
CREATE INDEX IF NOT EXISTS idx_edges_target      ON edges(target);
"""


def _has_fts5(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS _okf_fts5_test USING fts5(content='');")
        conn.execute("DROP TABLE IF EXISTS _okf_fts5_test;")
        return True
    except Exception:
        return False


def _parse_concept_md(path: Path, bundle_dir: Path) -> dict | None:
    """Parse a single .md concept file into a dict (same as lookup._parse_md)."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    if not text.startswith("---"):
        return None
    import re as _re
    m = _re.match(r"^---\s*\n(.*?)\n---", text, _re.DOTALL)
    if not m:
        return None
    fm_text = m.group(1)
    try:
        import yaml
        fm = yaml.safe_load(fm_text) or {}
    except Exception:
        return None
    ctype = fm.get("type", "")
    if not ctype or ctype in {"Index", "Log"}:
        return None
    body = text[m.end():].strip()
    sections: dict[str, str] = {}
    cur_key, cur_lines = None, []
    for line in body.splitlines():
        if line.startswith("## "):
            if cur_key:
                sections[cur_key] = "\n".join(cur_lines).strip()
            cur_key = line[3:].strip().lower()
            cur_lines = []
        elif cur_key is not None:
            cur_lines.append(line)
    if cur_key:
        sections[cur_key] = "\n".join(cur_lines).strip()
    rel = path.relative_to(bundle_dir)
    concept_id = str(rel.with_suffix("")).replace(os.sep, "/")
    lang = ""
    for t in fm.get("tags", []):
        if isinstance(t, str) and t.startswith("lang:") and t != "lang:manifest":
            lang = t[5:]
            break
    return {
        "concept_id": concept_id,
        "type": ctype,
        "title": fm.get("title", path.stem),
        "description": fm.get("description", ""),
        "resource": fm.get("resource", ""),
        "language": lang,
        "file_path": str(rel),
        "file_mtime": int(path.stat().st_mtime_ns),
        "content_hash": "",
        "sections_json": json.dumps(sections, ensure_ascii=False),
        "timestamp": fm.get("timestamp", ""),
        "raw": text,
        "tags": fm.get("tags", []),
    }


def _extract_edges(raw_text: str, concept_id: str) -> list[tuple[str, str, str]]:
    """Extract edges from markdown concept body. Returns [(source, target, reltype)]."""
    edges = []
    # Split frontmatter from body
    parts = raw_text.split("---", 2)
    if len(parts) < 3:
        return edges
    body = parts[2]

    current_section = ""
    for line in body.splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip().lower()
            continue
        if current_section in ("related", "calls", "called by", "used by"):
            m = re.search(r"\]\(/(.+?)\.md\)", line)
            if m:
                target = m.group(1)
                if current_section == "related":
                    edges.append((concept_id, target, "related"))
                elif current_section == "calls":
                    edges.append((concept_id, target, "calls"))
                elif current_section == "called by":
                    edges.append((target, concept_id, "called_by"))
                elif current_section == "used by":
                    edges.append((target, concept_id, "uses"))
        elif current_section == "relationships":
            if line.startswith("|"):
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if len(cells) >= 2:
                    m = re.search(r"\(/([^)]+)\.md\)", cells[1])
                    if m:
                        edges.append((concept_id, m.group(1), cells[0].lower()))
    return edges


class SQLiteBundleStore(BundleStore):
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._conn.execute("PRAGMA cache_size=-64000;")
        self._conn.execute("PRAGMA temp_store=MEMORY;")
        self._conn.execute("PRAGMA mmap_size=268435456;")
        self._conn.execute("PRAGMA busy_timeout=5000;")
        self._conn.row_factory = sqlite3.Row

    def close(self):
        self._conn.close()

    # -- helpers --

    def _row_to_dict(self, row: sqlite3.Row | None) -> dict | None:
        if row is None:
            return None
        d = dict(row)
        if "sections_json" in d:
            d["sections"] = json.loads(d.pop("sections_json"))
        else:
            d["sections"] = {}
        if "tags" not in d:
            d["tags"] = self._get_tags(d["concept_id"])
        return d

    def _get_tags(self, concept_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT tag FROM concept_tags WHERE concept_id = ?", (concept_id,)
        ).fetchall()
        return [r["tag"] for r in rows]

    def _get_language(self, concept_id: str) -> str:
        row = self._conn.execute(
            "SELECT language FROM concepts WHERE concept_id = ?", (concept_id,)
        ).fetchone()
        return row["language"] if row else ""

    def _has_fts5(self) -> bool:
        v = self._conn.execute(
            "SELECT value FROM _meta WHERE key = 'fts5_available'"
        ).fetchone()
        return v is not None and v["value"] == "1"

    # -- interface --

    def get(self, concept_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM concepts WHERE concept_id = ?", (concept_id,)
        ).fetchone()
        return self._row_to_dict(row)

    def search(
        self,
        query: str = "",
        type_filter: str = "",
        tag_filters: list[str] | None = None,
        limit: int = 80,
        offset: int = 0,
    ) -> list[dict]:
        tag_filters = tag_filters or []
        has_fts = self._has_fts5()
        params: list = []
        where_parts: list[str] = []
        join_part = ""

        if query and has_fts:
            # FTS5: use MATCH for full-text search
            fts_query = " AND ".join(f'"{w}"' for w in query.split() if w)
            join_part = "JOIN concepts_fts fts ON concepts.rowid = fts.rowid"
            where_parts.append(f"concepts_fts MATCH ?")
            params.append(fts_query)
        elif query:
            # No FTS5: fall back to LIKE
            like_clauses = []
            for w in query.split():
                if not w: continue
                like_clauses.append("(title LIKE ? OR description LIKE ?)")
                params.extend([f"%{w}%", f"%{w}%"])
            if like_clauses:
                where_parts.append("(" + " AND ".join(like_clauses) + ")")

        if type_filter:
            where_parts.append("concepts.type = ?")
            params.append(type_filter)

        for tag in tag_filters:
            where_parts.append("""
                concepts.concept_id IN (
                    SELECT concept_id FROM concept_tags WHERE tag = ?
                )
            """)
            params.append(tag)

        where_sql = " AND ".join(where_parts) if where_parts else "1"
        order = "rank" if (query and has_fts) else "concepts.concept_id"
        sql = f"""
            SELECT concepts.* FROM concepts
            {join_part}
            WHERE {where_sql}
            ORDER BY {order}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def count(self, type_filter: str = "", tag_filter: str = "") -> int:
        params: list = []
        where = []
        if type_filter:
            where.append("type = ?")
            params.append(type_filter)
        if tag_filter:
            where.append("""
                concept_id IN (SELECT concept_id FROM concept_tags WHERE tag = ?)
            """)
            params.append(tag_filter)
        w = " AND ".join(where) if where else "1"
        row = self._conn.execute(f"SELECT COUNT(*) as c FROM concepts WHERE {w}", params).fetchone()
        return row["c"]

    def stream_all(self):
        cursor = self._conn.execute("SELECT * FROM concepts")
        while True:
            rows = cursor.fetchmany(1000)
            if not rows:
                break
            for r in rows:
                yield self._row_to_dict(r)

    def get_neighbors(self, concept_id: str) -> list[dict]:
        neighbor_ids = set()
        rows = self._conn.execute(
            "SELECT target FROM edges WHERE source = ? UNION SELECT source FROM edges WHERE target = ?",
            (concept_id, concept_id),
        ).fetchall()
        for r in rows:
            neighbor_ids.add(r[0])
        concepts = []
        for nid in neighbor_ids:
            c = self.get(nid)
            if c:
                concepts.append(c)
        return concepts

    def get_graph(self, max_nodes: int = 200, center: str | None = None) -> dict:
        total = self._conn.execute("SELECT COUNT(*) as c FROM concepts").fetchone()["c"]

        if center:
            center_exists = self._conn.execute(
                "SELECT 1 FROM concepts WHERE concept_id = ?", (center,)
            ).fetchone()
            if not center_exists:
                return {"nodes": [], "edges": [], "total": total, "shown": 0}

            # Get neighbors via edges
            neighbor_ids = set()
            edge_rows = self._conn.execute(
                """SELECT source, target FROM edges
                   WHERE source = ? OR target = ? LIMIT ?""",
                (center, center, max_nodes),
            ).fetchall()
            selected = {center}
            for r in edge_rows:
                if r["source"] != center:
                    selected.add(r["source"])
                if r["target"] != center:
                    selected.add(r["target"])
        else:
            # Degree-ranked: most connected nodes first
            degree_rows = self._conn.execute("""
                SELECT concept_id, COUNT(*) as degree FROM (
                    SELECT source AS concept_id FROM edges
                    UNION ALL
                    SELECT target AS concept_id FROM edges
                ) GROUP BY concept_id ORDER BY degree DESC LIMIT ?
            """, (max_nodes,)).fetchall()
            selected = {r["concept_id"] for r in degree_rows}
            # If not enough from edges, fill with non-Dependency concepts
            if len(selected) < max_nodes:
                extra = self._conn.execute("""
                    SELECT concept_id FROM concepts
                    WHERE type != 'Dependency'
                    ORDER BY concept_id LIMIT ?
                """, (max_nodes - len(selected),)).fetchall()
                selected.update(r["concept_id"] for r in extra if r["concept_id"] not in selected)

        # Fetch node details
        placeholders = ",".join("?" for _ in selected)
        node_rows = self._conn.execute(
            f"SELECT concept_id, title, type, description, resource FROM concepts WHERE concept_id IN ({placeholders})",
            list(selected),
        ).fetchall()
        # Fetch tags for selected nodes in batch
        tag_rows = self._conn.execute(
            f"SELECT concept_id, tag FROM concept_tags WHERE concept_id IN ({placeholders})",
            list(selected),
        ).fetchall()
        tags_by_id: dict[str, list[str]] = {}
        for r in tag_rows:
            tags_by_id.setdefault(r["concept_id"], []).append(r["tag"])
        nodes = []
        for r in node_rows:
            cid = r["concept_id"]
            nodes.append({
                "id": cid,
                "title": r["title"],
                "type": r["type"],
                "description": r["description"] or "",
                "resource": r["resource"] or "",
                "tags": tags_by_id.get(cid, []),
            })

        # Edges among selected nodes
        edge_rows = self._conn.execute(
            f"""SELECT source, target, reltype FROM edges
                WHERE source IN ({placeholders}) AND target IN ({placeholders})
                LIMIT 10000""",
            list(selected) + list(selected),
        ).fetchall()
        edges = [{"from": r["source"], "to": r["target"], "type": r["reltype"]} for r in edge_rows]

        return {"nodes": nodes, "edges": edges, "total": total, "shown": len(nodes)}

    def get_types(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT type, COUNT(*) as count FROM concepts GROUP BY type ORDER BY count DESC"
        ).fetchall()
        return [{"type": r["type"], "count": r["count"]} for r in rows]

    def get_languages(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT language, COUNT(*) as count FROM concepts WHERE language != '' GROUP BY language ORDER BY count DESC"
        ).fetchall()
        return [{"language": r["language"], "count": r["count"]} for r in rows]

    def get_info(self) -> dict:
        total = self._conn.execute("SELECT COUNT(*) as c FROM concepts").fetchone()["c"]
        types = {r["type"]: r["count"] for r in self._conn.execute(
            "SELECT type, COUNT(*) as count FROM concepts GROUP BY type"
        ).fetchall()}
        langs = {r["language"]: r["count"] for r in self._conn.execute(
            "SELECT language, COUNT(*) as count FROM concepts WHERE language != '' GROUP BY language"
        ).fetchall()}
        ecos = {}
        for r in self._conn.execute(
            "SELECT tag, COUNT(*) as count FROM concept_tags WHERE tag LIKE 'ecosystem:%' GROUP BY tag"
        ).fetchall():
            ecos[r["tag"][10:]] = r["count"]
        return {"name": "", "total": total, "types": types, "languages": langs, "ecosystems": ecos}

    @contextmanager
    def transaction(self):
        self._conn.execute("BEGIN")
        try:
            yield
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    # -- build / rebuild --

    @classmethod
    def build(cls, bundle_dir: Path, db_path: Path) -> "SQLiteBundleStore":
        db_path = Path(db_path)
        if db_path.exists():
            db_path.unlink()

        store = cls(db_path)
        conn = store._conn

        # Create tables
        conn.executescript(SQL_CREATE_TABLES)

        # Detect FTS5
        fts5 = _has_fts5(conn)
        conn.execute("INSERT OR REPLACE INTO _meta VALUES ('fts5_available', ?)", ("1" if fts5 else "0",))

        if fts5:
            try:
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
                        title, description,
                        content='concepts', content_rowid='rowid',
                        tokenize='porter unicode61'
                    )
                """)
            except Exception:
                fts5 = False
                conn.execute("INSERT OR REPLACE INTO _meta VALUES ('fts5_available', '0')")

        reserved = {"index.md", "log.md", "SUMMARY.md"}
        concept_rows: list[tuple] = []
        tag_rows: list[tuple] = []
        edge_rows: list[tuple] = []

        from pathlib import Path as _P
        md_files = sorted(bundle_dir.rglob("*.md"))

        # Pre-scan all md files for fingerprinting (fast)
        md_count = 0
        md_latest_mtime = 0
        md_file_list = []
        for md_path in md_files:
            if md_path.name in reserved:
                continue
            md_count += 1
            mt = md_path.stat().st_mtime_ns
            if mt > md_latest_mtime:
                md_latest_mtime = mt
            md_file_list.append(md_path)

        with conn:
            for md_path in md_file_list:
                parsed = _parse_concept_md(md_path, bundle_dir)
                if not parsed:
                    continue
                concept_rows.append((
                    parsed["concept_id"], parsed["type"], parsed["title"],
                    parsed["description"], parsed["resource"], parsed["language"],
                    parsed["file_path"], parsed["file_mtime"],
                    parsed["sections_json"], parsed["timestamp"],
                ))
                for tag in parsed.get("tags", []):
                    if isinstance(tag, str):
                        tag_rows.append((parsed["concept_id"], tag))
                for src, tgt, rt in _extract_edges(parsed["raw"], parsed["concept_id"]):
                    edge_rows.append((src, tgt, rt))

            # Batch insert concepts
            conn.executemany("""
                INSERT OR REPLACE INTO concepts
                (concept_id, type, title, description, resource, language,
                 file_path, file_mtime, sections_json, timestamp)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, concept_rows)

            # Batch insert tags
            conn.executemany(
                "INSERT OR REPLACE INTO concept_tags (concept_id, tag) VALUES (?,?)",
                tag_rows,
            )

            # Batch insert edges
            conn.executemany(
                "INSERT OR REPLACE INTO edges (source, target, reltype) VALUES (?,?,?)",
                edge_rows,
            )

            # FTS5 rebuild
            if fts5:
                try:
                    conn.execute("INSERT INTO concepts_fts(concepts_fts) VALUES('rebuild')")
                except Exception:
                    pass

        # Metadata (use pre-scan counts for reliable fingerprint)
        conn.execute(
            "INSERT OR REPLACE INTO _meta VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        conn.execute(
            "INSERT OR REPLACE INTO _meta VALUES ('total_files', ?)", (str(md_count),),
        )
        conn.execute(
            "INSERT OR REPLACE INTO _meta VALUES ('latest_mtime', ?)", (str(md_latest_mtime),),
        )
        conn.execute(
            "INSERT OR REPLACE INTO _meta VALUES ('build_timestamp', ?)",
            (str(int(time.time())),),
        )
        conn.commit()

        return store

    # -- fingerprint / freshness --

    @staticmethod
    def db_is_fresh(db_path: Path, bundle_dir: Path) -> bool:
        if not db_path.exists():
            return False
        try:
            conn = sqlite3.connect(str(db_path))
            row = conn.execute(
                "SELECT value FROM _meta WHERE key = 'schema_version'"
            ).fetchone()
            if not row or int(row[0]) != SCHEMA_VERSION:
                conn.close()
                return False
            total_row = conn.execute(
                "SELECT value FROM _meta WHERE key = 'total_files'"
            ).fetchone()
            mtime_row = conn.execute(
                "SELECT value FROM _meta WHERE key = 'latest_mtime'"
            ).fetchone()
            conn.close()
            if not total_row or not mtime_row:
                return False
            stored_total = int(total_row[0])
            stored_mtime = int(mtime_row[0])
        except Exception:
            return False

        # Fast check: count md files, check latest mtime
        reserved = {"index.md", "log.md", "SUMMARY.md"}
        current_count = 0
        current_latest = 0
        try:
            for entry in bundle_dir.rglob("*.md"):
                if entry.name in reserved:
                    continue
                current_count += 1
                mt = entry.stat().st_mtime_ns
                if mt > current_latest:
                    current_latest = mt
        except Exception:
            return False

        return current_count == stored_total and current_latest == stored_mtime

    # -- incremental update stubs --

    def update_file(self, path: Path):
        raise NotImplementedError("Incremental update via SQLite — coming in next phase")

    def remove_file(self, path: Path):
        raise NotImplementedError("Incremental update via SQLite — coming in next phase")

    def rebuild(self, bundle_dir: Path):
        self.close()
        db_path = self._db_path
        if db_path.exists():
            db_path.unlink()
        new_store = self.build(bundle_dir, db_path)
        self._conn = new_store._conn
        self._db_path = new_store._db_path
