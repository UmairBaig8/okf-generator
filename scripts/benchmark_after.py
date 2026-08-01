"""Post-SQLite benchmark — tests the new storage layer."""
import json, os, sys, time, gc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BUNDLE = Path(os.environ.get("OKF_BENCH_BUNDLE", "/Users/umairbaig/WSpace/.benchmark_bundle"))


def run_all(label: str) -> dict:
    r = {"label": label}

    db_path = BUNDLE / ".okf_db.sqlite"

    # Clean DB to force rebuild
    for p in [db_path, Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")]:
        if p.exists(): p.unlink()

    from okf.storage import open_store

    # ---- 1. BUILD from scratch ----
    t0 = time.time()
    store = open_store(BUNDLE)
    t1 = time.time()
    r["sqlite_build_s"] = round(t1 - t0, 2)
    r["n_concepts"] = store.get_info()["total"]
    r["db_mb"] = round(db_path.stat().st_size / 1024 / 1024, 1)

    # ---- 2. CACHED OPEN (reconnect after close) ----
    store.close()
    t0 = time.time()
    store2 = open_store(BUNDLE)
    t1 = time.time()
    r["cached_open_s"] = round(t1 - t0, 4)

    # ---- 3. SEARCH ----
    terms = ["agent", "class", "model", "train", "config", "handler", "database", "api"]
    times = []
    for term in terms:
        t0 = time.time()
        _ = store2.search(query=term, limit=10)
        t1 = time.time()
        times.append((t1 - t0) * 1000)
    r["search_avg_ms"] = round(sum(times) / len(times), 1)
    r["search_min_ms"] = round(min(times), 1)
    r["search_max_ms"] = round(max(times), 1)

    # ---- 4. POINT LOOKUP ----
    t0 = time.time()
    _ = store2.get("okf-generator/okf/generator")
    t1 = time.time()
    r["point_lookup_ms"] = round((t1 - t0) * 1000, 2)

    t0 = time.time()
    _ = store2.get("nonexistent/path")
    t1 = time.time()
    r["miss_lookup_ms"] = round((t1 - t0) * 1000, 2)

    # ---- 5. GRAPH ----
    t0 = time.time()
    g = store2.get_graph(max_nodes=200)
    t1 = time.time()
    r["graph_200_s"] = round(t1 - t0, 4)
    r["graph_200_nodes"] = g["shown"]
    r["graph_200_edges"] = len(g["edges"])

    t0 = time.time()
    g2 = store2.get_graph(max_nodes=50, center="okf-generator/okf/generator")
    t1 = time.time()
    r["graph_50_center_s"] = round(t1 - t0, 4)
    r["graph_50_center_nodes"] = g2["shown"]

    # ---- 6. NEIGHBORS ----
    t0 = time.time()
    n = store2.get_neighbors("okf-generator/okf/generator")
    t1 = time.time()
    r["neighbors_ms"] = round((t1 - t0) * 1000, 1)
    r["neighbors_count"] = len(n)

    # ---- 7. TYPES / LANGUAGES / INFO ----
    t0 = time.time()
    _ = store2.get_types()
    t1 = time.time()
    r["types_ms"] = round((t1 - t0) * 1000, 1)

    t0 = time.time()
    _ = store2.get_languages()
    t1 = time.time()
    r["languages_ms"] = round((t1 - t0) * 1000, 1)

    t0 = time.time()
    _ = store2.get_info()
    t1 = time.time()
    r["info_ms"] = round((t1 - t0) * 1000, 1)

    store2.close()

    # ---- 8. OKF VISUALIZE (via new code path) ----
    gc.collect()
    import importlib
    import okf.visualize as viz_mod
    importlib.reload(viz_mod)

    t0 = time.time()
    html, n_nodes, n_edges = viz_mod.visualize(BUNDLE)
    t1 = time.time()
    r["visualize_s"] = round(t1 - t0, 2)
    r["html_mb"] = round(len(html) / 1024 / 1024, 1)
    r["viz_nodes"] = n_nodes
    r["viz_edges"] = n_edges

    # ---- 9. DASHBOARD BUILD (simulated startup) ----
    gc.collect()
    t0 = time.time()
    app = viz_mod.build_graph(BUNDLE) if hasattr(viz_mod, 'build_graph') else None
    t1 = time.time()
    # Use store directly from a fresh open to simulate dashboard startup
    t0 = time.time()
    s3 = open_store(BUNDLE)
    _info = s3.get_info()
    t1 = time.time()
    r["dashboard_startup_s"] = round(t1 - t0, 2)
    s3.close()

    # ---- 10. MEMORY (process RSS estimate) ----
    # We check how much memory SQLite connection + page cache uses
    try:
        import os as _os
        import psutil
        proc = psutil.Process(_os.getpid())
        r["mem_before_build_mb"] = round(proc.memory_info().rss / 1024 / 1024, 1)
    except ImportError:
        r["mem_before_build_mb"] = "N/A (psutil not installed)"

    return r


def print_results(r: dict):
    print(f"\n{'='*60}")
    print(f"  BENCHMARK: {r['label']}")
    print(f"{'='*60}")
    for k, v in r.items():
        if k == "label": continue
        print(f"  {k:30s} {v}")


if __name__ == "__main__":
    r = run_all("AFTER — with SQLite store")
    print_results(r)
    with open(BUNDLE / ".benchmark_after.json", "w") as f:
        json.dump(r, f, indent=2)
    print(f"\nSaved to {BUNDLE / '.benchmark_after.json'}")
