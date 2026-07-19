"""okf serve — launch a local HTTP server for an OKF bundle viz.

Supports local directories and git repository URLs:

  okf serve ./okf_bundle
  okf serve https://github.com/user/repo.git@main
  okf serve https://github.com/user/repo.git@main --generate
  okf serve ./src --generate
  okf serve --stop
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import os
import re
import socketserver
import subprocess
import sys
import webbrowser
from pathlib import Path

from okf.config import load as load_config, _get

_cfg = load_config()
PORT = _get(_cfg, "serve.port", 8000)
HOST = _get(_cfg, "serve.host", "127.0.0.1")
PID_DIR = Path.home() / ".cache" / "okf"
PID_FILE = PID_DIR / "serve.pid"
REPOS_CACHE = PID_DIR / "repos"

_GIT_URL_RE = re.compile(
    r"^(?:(https?://|git@|ssh://)|)"  # optional protocol
    r"([a-zA-Z0-9._-]+(?:\.[a-zA-Z0-9._-]+)+)"  # host
    r"[:/]"  # separator
    r"([a-zA-Z0-9._/-]+?)"  # path
    r"(?:\.git)?$"  # optional .git suffix
)


def write_pid():
    PID_DIR.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))


def read_pid() -> int | None:
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except (ValueError, OSError):
            return None
    return None


def stop_server(silent=False):
    pid = read_pid()
    if pid is not None:
        try:
            os.kill(pid, 15)
            if not silent:
                print(f"  Stopped previous server (PID {pid}).")
        except ProcessLookupError:
            pass
    PID_FILE.unlink(missing_ok=True)


def _is_git_url(s: str) -> bool:
    if s.startswith(("https://", "http://", "git@", "ssh://")):
        return True
    if s.endswith(".git"):
        return True
    if re.match(r"^[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+[:/]", s):
        return True
    return False


def _parse_git_url(raw: str) -> tuple[str, str]:
    """Parse a git URL with optional @ref. Returns (clone_url, ref)."""
    ref = "HEAD"
    url = raw
    if "@" in raw:
        parts = raw.rsplit("@", 1)
        if not parts[0].startswith(("https://", "http://", "git@", "ssh://")):
            if "/" not in parts[1]:
                url, ref = parts
            else:
                url = raw
        else:
            if "/" not in parts[1] and "." not in parts[1]:
                url, ref = parts
    if not url.startswith(("https://", "http://", "git@", "ssh://")):
        url = f"https://{url}"
    if not url.endswith(".git"):
        url = f"{url}.git"
    return url, ref


def _cache_dir(url: str) -> Path:
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    return REPOS_CACHE / h


def _clone_or_update(url: str, ref: str, update: bool) -> Path:
    dest = _cache_dir(url)
    if dest.exists():
        if update:
            subprocess.run(["git", "-C", str(dest), "fetch", "--all", "-q"], check=False)
            if ref != "HEAD":
                subprocess.run(["git", "-C", str(dest), "checkout", "-q", ref], check=False)
            else:
                subprocess.run(["git", "-C", str(dest), "pull", "-q"], check=False)
            print(f"  Updated: {url} @ {ref}")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Cloning {url} @ {ref}...")
    subprocess.run(
        ["git", "clone", "-q", url, str(dest)],
        check=True, capture_output=True, timeout=120,
    )
    if ref != "HEAD":
        result = subprocess.run(["git", "-C", str(dest), "checkout", "-q", ref], check=False, timeout=60)
        if result.returncode != 0:
            print(f"  ERROR: ref {ref!r} not found in {url}", file=sys.stderr)
            print(f"  Available refs: run 'git ls-remote {url}' to list branches/tags", file=sys.stderr)
            sys.exit(1)
    print(f"  Cloned → {dest}")
    return dest


def _has_bundle_marker(directory: Path) -> bool:
    return (directory / "okf_bundle" / "index.md").exists()


def _resolve_bundle(directory: Path, generate: bool) -> Path | None:
    """Check for existing bundle; optionally generate if missing.

    Returns bundle subdir path if found/generated, None to serve root.
    """
    bundle_sub = directory / "okf_bundle"
    if _has_bundle_marker(directory):
        return bundle_sub
    if generate:
        print(f"  No bundle found — generating (this may take a while)...")
        try:
            result = subprocess.run(
                ["okf", "generate", str(directory), str(bundle_sub)],
                capture_output=True, text=True, timeout=600,
            )
            if result.returncode != 0:
                print(f"  WARNING: okf generate failed:", file=sys.stderr)
                for line in result.stderr.splitlines()[-5:]:
                    print(f"    {line}")
                print(f"  Serving source tree instead.")
                return None
            print(f"  Bundle generated → {bundle_sub}")
            return bundle_sub
        except FileNotFoundError:
            print(f"  WARNING: 'okf' not found on PATH. Cannot generate bundle.")
            print(f"  Run 'okf generate {directory} {bundle_sub}' manually.")
            return None
        except subprocess.TimeoutExpired:
            print(f"  ERROR: generation timed out (10 min limit).")
            print(f"  Run 'okf generate {directory} {bundle_sub}' manually.")
            return None
    return None


class VizzHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" and os.path.exists("viz.html"):
            self.send_response(302)
            self.send_header("Location", "/viz.html")
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Launch a local HTTP server for an OKF bundle visualization.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("bundle_dir", nargs="?", default="./okf_bundle",
                        help="Directory or git URL to serve (default: ./okf_bundle)")
    parser.add_argument("--port", "-p", type=int, default=PORT, help=f"Port (default: {PORT})")
    parser.add_argument("--host", default=HOST, help=f"Host (default: {HOST})")
    parser.add_argument("--open", "-o", action="store_true", help="Open browser automatically")
    parser.add_argument("--stop", action="store_true", help="Stop a running server")
    parser.add_argument("--update", action="store_true", help="Fetch latest from git remote before serving")
    parser.add_argument("--generate", action="store_true", help="Run okf generate if bundle missing (first clone only)")
    args = parser.parse_args()

    if args.stop:
        stop_server()
        sys.exit(0)

    stop_server(silent=True)

    # Resolve directory — may be a git URL
    raw = args.bundle_dir
    if _is_git_url(raw):
        url, ref = _parse_git_url(raw)
        print(f"  Git repo: {url} @ {ref}")
        directory = _clone_or_update(url, ref, update=args.update)
        if directory is None or not directory.exists():
            print(f"ERROR: Failed to clone/fetch {url}", file=sys.stderr)
            sys.exit(1)
    else:
        directory = Path(raw).resolve()
        if not directory.exists():
            print(f"ERROR: Directory not found: {directory}", file=sys.stderr)
            sys.exit(1)

    # Check for existing bundle, optionally auto-generate
    bundle_dir = _resolve_bundle(directory, generate=args.generate)
    if bundle_dir is not None:
        directory = bundle_dir

    os.chdir(directory)

    if not os.path.exists("viz.html"):
        bundle_marker = directory / "index.md"
        if bundle_marker.exists():
            print(f"  Generating viz.html from {directory.name}...")
            try:
                result = subprocess.run(["okf", "visualize", str(directory)], capture_output=True, text=True, timeout=120)
                if result.returncode != 0:
                    print(f"  WARNING: visualize failed (run 'okf visualize {directory}' manually)")
                else:
                    print(f"  {result.stdout.strip()}")
            except FileNotFoundError:
                print(f"  WARNING: 'okf' not found on PATH. Run 'okf visualize {directory}' manually.")
            except subprocess.TimeoutExpired:
                print(f"  WARNING: visualize timed out. Run 'okf visualize {directory}' manually.")

    url = f"http://{args.host}:{args.port}/viz.html"
    has_viz = os.path.exists("viz.html")
    if has_viz:
        print(f"  OKF Viz: {url}")
    else:
        print(f"  No viz.html found in {directory.name}.")
        print(f"  {url.replace('/viz.html', '')}")

    write_pid()

    if args.open and has_viz:
        webbrowser.open(url)
    elif args.open:
        webbrowser.open(f"http://{args.host}:{args.port}")

    print(f"  Serving {directory} on {args.host}:{args.port}")

    try:
        with socketserver.TCPServer((args.host, args.port), VizzHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        PID_FILE.unlink(missing_ok=True)
        sys.exit(0)
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
