"""watchdog-based file watcher for okf update --watch.

Debounces rapid save bursts, filters editor temp-file patterns,
and triggers incremental updates on detected changes.
"""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

log = logging.getLogger("okf_watcher")

# Extensions we care about (configurable via .okfconfig update.watch_extensions)
DEFAULT_WATCH_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".rs", ".java", ".rb", ".kt", ".swift",
    ".sql", ".yaml", ".yml", ".json", ".toml",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".dart",
    ".scala", ".jl", ".php", ".rb",
}

# Editor temp-file patterns to ignore
IGNORE_PATTERNS = {
    "*.swp", "*.swo", "*.swx",       # vim
    ".*.swp", ".*.swo",              # vim (hidden)
    "#*#",                            # emacs
    ".#*",                            # emacs lock
    ".~*",                            # office/libreoffice
    "~$*",                            # office temp
    "*.tmp", "*.TMP",                 # generic temp
    ".DS_Store", "Thumbs.db",         # OS metadata
    "*.pyc", "*.pyo",                 # python bytecode
    "*.bak", "*.orig",                # backup files
}


def _load_watch_ignore_patterns(source_root: Path) -> list:
    from okf.ignore import load_patterns
    pats = load_patterns(source_root)
    return pats


def watch_and_update(
    source_root: Path,
    bundle_dir: Path,
    debounce_ms: int = 500,
    exclude: set[str] | None = None,
    enable_enrich: bool = False,
):
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler

    exclude = exclude or set()
    ignore_pats = _load_watch_ignore_patterns(source_root)
    timer: threading.Timer | None = None
    timer_lock = threading.Lock()

    def _run_update():
        from okf.update import update_bundle
        log.info("Change detected — running incremental update...")
        try:
            dirty = update_bundle(source_root, bundle_dir, exclude, force=False, enable_enrich=enable_enrich)
            if dirty > 0:
                log.info(f"Updated {dirty} concept(s)")
            else:
                log.info("No changes to write")
        except Exception as e:
            log.error(f"Update failed: {e}", exc_info=True)

    def _debounce_trigger(event):
        nonlocal timer
        src_path = getattr(event, "src_path", "")
        if src_path:
            for pat in IGNORE_PATTERNS:
                fnmatch = __import__("fnmatch")
                if fnmatch.fnmatch(src_path, pat):
                    return
            rel = Path(src_path).relative_to(source_root) if source_root in Path(src_path).parents else None
            if rel is not None:
                from okf.ignore import matches
                if matches(rel, ignore_pats):
                    return

        ext = Path(src_path).suffix.lower() if src_path else ""
        exts = DEFAULT_WATCH_EXTENSIONS
        if ext and ext not in exts:
            return

        if ext in {".json", ".toml", ".yml", ".yaml"}:
            pass

        with timer_lock:
            nonlocal timer
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(debounce_ms / 1000.0, _run_update)
            timer.daemon = True
            timer.start()

    patterns = ["*"]
    ignore_patterns = list(IGNORE_PATTERNS)

    event_handler = PatternMatchingEventHandler(
        patterns=patterns,
        ignore_patterns=ignore_patterns,
        ignore_directories=True,
        case_sensitive=False,
    )
    event_handler.on_created = _debounce_trigger
    event_handler.on_modified = _debounce_trigger

    observer = Observer()
    observer.schedule(event_handler, str(source_root), recursive=True)
    observer.start()

    log.info(f"Watching {source_root} (debounce={debounce_ms}ms)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
