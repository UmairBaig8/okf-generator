"""Benchmark OKF bundle loading/search/visualize — before and after SQLite."""
import json, os, re, sys, time, gc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BUNDLE = Path(os.environ.get("OKF_BENCH_BUNDLE", "/Users/umairbaig/WSpace/.benchmark_bundle"))


def mem_estimate(objs: list) -> float:
    import sys as _sys
    total = 0
    seen = set()
    for o in objs:
        oid = id(o)
        if oid in seen: continue
        seen.add(oid)
        total += _sys.getsizeof(o)
        if isinstance(o, dict):
            for k, v in o.items():
                total += _sys.getsizeof(k)
                total += _sys.getsizeof(v)
    return total / 1024 / 1024


def run_all(label: str) -> dict:
    r = {"label": label}

    # ---- 1. cold load (no cache) ----
    cache_path = BUNDLE / ".okf_lookup_cache.json"
    db_path = BUNDLE / ".okf_db.sqlite"
    if cache_path.exists(): cache_path.unlink()
    if db_path.exists(): db_path.unlink()

    t0 = time.time()
    from okf.lookup import load_bundle
    concepts = load_bundle(BUNDLE, use_cache=False)
    t1 = time.time()
    r["cold_load_s"] = round(t1 - t0, 2)
    r["n_concepts"] = len(concepts)
    r["mem_mb"] = round(mem_estimate([concepts]), 1)
    # also include by_id overhead
    by_id = {c["concept_id"]: c for c in concepts}
    r["mem_with_byid_mb"] = round(mem_estimate([concepts, by_id]), 1)

    # md file count
    r["md_files"] = len(list(BUNDLE.rglob("*.md")))

    # ---- 2. cached load (if applicable) ----
    if cache_path.exists():
        t0 = time.time()
        concepts2 = load_bundle(BUNDLE, use_cache=True)
        t1 = time.time()
        r["cached_load_s"] = round(t1 - t0, 4)
        r["cache_kb"] = round(cache_path.stat().st_size / 1024, 0)
    if db_path.exists():
        r["db_mb"] = round(db_path.stat().st_size / 1024 / 1024, 1)

    # ---- 3. search (multiple queries) ----
    from okf.lookup import search
    terms = ["agent", "class", "model", "train", "config", "handler", "database", "api"]
    times = []
    for term in terms:
        t0 = time.time()
        _ = search(concepts, tokens=[term], limit=10)
        t1 = time.time()
        times.append((t1 - t0) * 1000)
    r["search_avg_ms"] = round(sum(times) / len(times), 1)
    r["search_min_ms"] = round(min(times), 1)
    r["search_max_ms"] = round(max(times), 1)

    # ---- 4. build_graph ----
    gc.collect()
    from okf.visualize import build_graph
    t0 = time.time()
    nodes, links, bundles_list, counts = build_graph(BUNDLE)
    t1 = time.time()
    r["build_graph_s"] = round(t1 - t0, 2)
    r["graph_nodes"] = len(nodes)
    r["graph_edges"] = len(links)
    del nodes, links, bundles_list, counts

    # ---- 5. visualize HTML ----
    gc.collect()
    from okf.visualize import visualize
    t0 = time.time()
    html, n_nodes, n_edges = visualize(BUNDLE)
    t1 = time.time()
    r["visualize_s"] = round(t1 - t0, 2)
    r["html_mb"] = round(len(html) / 1024 / 1024, 1)

    # ---- 6. dashboard startup sim ----
    gc.collect()
    t0 = time.time()
    from okf.lookup import load_bundle as lb2
    _c2 = lb2(BUNDLE, use_cache=True)
    _by_id = {c["concept_id"]: c for c in _c2}
    t1 = time.time()
    r["dashboard_startup_s"] = round(t1 - t0, 2)

    return r


def print_results(r: dict):
    print(f"\n{'='*60}")
    print(f"  BENCHMARK: {r['label']}")
    print(f"{'='*60}")
    for k, v in r.items():
        if k == "label": continue
        print(f"  {k:25s} {v}")


if __name__ == "__main__":
    r = run_all("BEFORE — current code")
    print_results(r)
    with open(BUNDLE / ".benchmark_before.json", "w") as f:
        json.dump(r, f, indent=2)
    print(f"\nSaved to {BUNDLE / '.benchmark_before.json'}")
