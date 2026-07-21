import re
from pathlib import Path

from okf.storage.base import BundleStore
from okf.lookup import search as _search


class MemoryBundleStore(BundleStore):
    def __init__(self, concepts: list[dict]):
        self._concepts = concepts
        self._by_id = {c["concept_id"]: c for c in concepts}

    def close(self):
        self._concepts.clear()
        self._by_id.clear()

    def get(self, concept_id: str) -> dict | None:
        return self._by_id.get(concept_id)

    def search(
        self,
        query: str = "",
        type_filter: str = "",
        tag_filters: list[str] | None = None,
        limit: int = 80,
        offset: int = 0,
    ) -> list[dict]:
        tokens = query.split() if query else []
        results = _search(
            self._concepts,
            tokens=tokens,
            type_filter=type_filter,
            tag_filters=tag_filters or [],
            limit=limit + offset,
        )
        return results[offset:]

    def count(self, type_filter: str = "", tag_filter: str = "") -> int:
        n = 0
        for c in self._concepts:
            if type_filter and c["type"].lower() != type_filter.lower():
                continue
            if tag_filter:
                ctags = [t.lower() for t in c.get("tags", [])]
                if tag_filter.lower() not in ctags:
                    continue
            n += 1
        return n

    def stream_all(self):
        yield from self._concepts

    def get_neighbors(self, concept_id: str) -> list[dict]:
        neighbors = {}
        for c in self._concepts:
            cid = c["concept_id"]
            secs = c.get("sections", {})
            for rel_type in ("related", "calls"):
                for line in secs.get(rel_type, "").splitlines():
                    m = re.search(r"\]\(/(.+?)\.md\)", line)
                    if m:
                        if m.group(1) == concept_id:
                            neighbors[cid] = c
                        if cid == concept_id:
                            n = self._by_id.get(m.group(1))
                            if n:
                                neighbors[m.group(1)] = n
            for line in secs.get("called by", "").splitlines():
                m = re.search(r"\]\(/(.+?)\.md\)", line)
                if m:
                    if m.group(1) == concept_id:
                        neighbors[cid] = c
                    if cid == concept_id:
                        n = self._by_id.get(m.group(1))
                        if n:
                            neighbors[m.group(1)] = n
        return list(neighbors.values())

    def get_graph(self, max_nodes: int = 200, center: str | None = None) -> dict:
        if center:
            center_c = self._by_id.get(center)
            if not center_c:
                return {"nodes": [], "edges": [], "total": len(self._concepts), "shown": 0}
            selected = {center}
            neighbors = self.get_neighbors(center)
            for n in neighbors[: max_nodes - 1]:
                selected.add(n["concept_id"])
        else:
            scored = [
                (
                    c["type"] != "Dependency",
                    sum(1 for t in c.get("tags", []) if t.startswith("lang:")),
                    c["concept_id"],
                )
                for c in self._concepts
            ]
            ranked = [c for _, c in sorted(zip(scored, self._concepts), key=lambda x: (-x[0][0], -x[0][1], x[0][2]))]
            selected = {c["concept_id"] for c in ranked[:max_nodes]}

        nodes = [
            {"id": c["concept_id"], "label": c["title"], "title": f"{c['type']}: {c['title']}", "group": c["type"]}
            for c in self._concepts
            if c["concept_id"] in selected
        ]

        edges = []
        for c in self._concepts:
            cid = c["concept_id"]
            if cid not in selected:
                continue
            secs = c.get("sections", {})
            for rel_type in ("related", "calls"):
                for line in secs.get(rel_type, "").splitlines():
                    m = re.search(r"\]\(/(.+?)\.md\)", line)
                    if m and m.group(1) in selected:
                        edges.append({"from": cid, "to": m.group(1), "type": rel_type})
            for line in secs.get("called by", "").splitlines():
                m = re.search(r"\]\(/(.+?)\.md\)", line)
                if m and m.group(1) in selected:
                    edges.append({"from": m.group(1), "to": cid, "type": "called_by"})
        return {"nodes": nodes, "edges": edges, "total": len(self._concepts), "shown": len(nodes)}

    def get_types(self) -> list[dict]:
        types: dict[str, int] = {}
        for c in self._concepts:
            types[c["type"]] = types.get(c["type"], 0) + 1
        return [{"type": k, "count": v} for k, v in sorted(types.items(), key=lambda x: -x[1])]

    def get_languages(self) -> list[dict]:
        langs: dict[str, int] = {}
        for c in self._concepts:
            for t in c.get("tags", []):
                if t.startswith("lang:") and t != "lang:manifest":
                    lang = t[5:]
                    langs[lang] = langs.get(lang, 0) + 1
        return [{"language": k, "count": v} for k, v in sorted(langs.items(), key=lambda x: -x[1])]

    def get_info(self) -> dict:
        types: dict[str, int] = {}
        langs: dict[str, int] = {}
        ecosystems: dict[str, int] = {}
        for c in self._concepts:
            types[c["type"]] = types.get(c["type"], 0) + 1
            for t in c.get("tags", []):
                if t.startswith("lang:") and t != "lang:manifest":
                    langs[t[5:]] = langs.get(t[5:], 0) + 1
                if t.startswith("ecosystem:"):
                    ecosystems[t[10:]] = ecosystems.get(t[10:], 0) + 1
        return {
            "name": "",
            "total": len(self._concepts),
            "types": types,
            "languages": langs,
            "ecosystems": ecosystems,
        }

    def transaction(self):
        class _NoopCtx:
            def __enter__(self2): return self2
            def __exit__(self2, *a): pass
        return _NoopCtx()

    def rebuild(self, bundle_dir: Path):
        raise NotImplementedError("MemoryBundleStore cannot rebuild")

    def update_file(self, path: Path):
        raise NotImplementedError("MemoryBundleStore does not support incremental update")

    def remove_file(self, path: Path):
        raise NotImplementedError("MemoryBundleStore does not support incremental update")
