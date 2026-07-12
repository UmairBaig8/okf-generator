"""YAML parser using PyYAML. Handles multi-doc (---) and stores raw parsed
dict in body_extra.yaml_doc for the domain classification engine."""

from pathlib import Path

import yaml

from okf.parsers.base import Concept, log, _ts, _first_line


class YamlParser:
    LANGUAGE   = "yaml"
    EXTENSIONS = {".yaml", ".yml"}

    def parse_file(self, path: Path, repo_root: Path) -> list[Concept]:
        rel = str(path.relative_to(repo_root))
        ts  = _ts(path)
        res_id = str(path.relative_to(repo_root).with_suffix("")).replace("/", "/")

        try:
            src = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            log.debug(f"Failed to read {path}: {e}")
            return [Concept(
                type="Module", title=path.stem, resource=rel,
                description=f"YAML file (read error: {e})",
                tags=["yaml"], timestamp=ts,
                concept_id=res_id,
            )]

        try:
            docs = list(yaml.safe_load_all(src))
        except Exception as e:
            log.debug(f"YAML parse error in {path}: {e}")
            return [Concept(
                type="Module", title=path.stem, resource=rel,
                description=f"YAML file (parse error: {e})",
                tags=["yaml"], timestamp=ts,
                concept_id=res_id,
            )]

        # Filter out None/empty docs
        docs = [d for d in docs if isinstance(d, dict)]

        if not docs:
            return [Concept(
                type="Module", title=path.stem, resource=rel,
                description=f"YAML file: {path.name}",
                tags=["yaml"], timestamp=ts,
                concept_id=res_id,
            )]

        module_title = path.stem
        module = Concept(
            type="Module",
            title=module_title,
            description=f"YAML file: {path.name} ({len(docs)} document(s))",
            resource=rel,
            tags=["yaml", module_title],
            timestamp=ts,
            concept_id=res_id,
        )

        concepts = [module]
        for i, doc in enumerate(docs):
            title = doc.get("kind") or doc.get("name") or doc.get("apiVersion", "").split("/")[0] or f"doc-{i}"
            title = str(title)
            desc = _first_line(str(doc.get("metadata", {}).get("description", "")))
            sig = doc.get("apiVersion", "")
            if sig and doc.get("kind"):
                sig = f"{sig}/{doc['kind']}"

            cid = f"{res_id}/{_safe_id(title)}-{i}" if i > 0 else f"{res_id}/{_safe_id(title)}"
            resource_concept = Concept(
                type="Resource",
                title=title,
                description=desc or f"{' | '.join(k for k in list(doc.keys())[:3])}",
                resource=rel,
                tags=["yaml", "resource"],
                timestamp=ts,
                signature=sig,
                concept_id=cid,
                related=[module.concept_id],
                body_extra={"yaml_doc": doc},
            )
            module.related.append(resource_concept.concept_id)
            concepts.append(resource_concept)

        return concepts


def _safe_id(name: str) -> str:
    import re
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", str(name)).strip("_") or "unknown"
