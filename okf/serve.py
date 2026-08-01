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

from okf import __version__
from okf.config import _get
from okf.config import load as load_config

_cfg = load_config()
PORT = _get(_cfg, "serve.port", 8000)
HOST = _get(_cfg, "serve.host", "127.0.0.1")
PID_DIR = Path.home() / ".cache" / "okf"
PID_FILE = PID_DIR / "serve.pid"
REPOS_CACHE = PID_DIR / "repos"

_GIT_URL_RE = re.compile(
    r"^https://"  # https only — never ssh:// or git@ (SSRF / subprocess injection)
    r"([a-zA-Z0-9._-]+(?:\.[a-zA-Z0-9._-]+)+)"  # host
    r"[:/]"  # separator
    r"([a-zA-Z0-9._/-]+?)"  # path
    r"(?:\.git)?$"  # optional .git suffix
)

_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _is_loopback(host: str) -> bool:
    return host in _LOOPBACK_HOSTS or host.startswith("127.")


def write_pid():
    PID_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Refuse to clobber a symlink (pre-existing-file symlink attack in shared cache dir)
    try:
        if PID_FILE.is_symlink() or (PID_FILE.exists() and not PID_FILE.is_file()):
            print("  WARNING: serve.pid exists as a symlink/non-regular file; not writing PID.", file=sys.stderr)
            return
        PID_FILE.write_text(str(os.getpid()))
    except OSError as e:
        print(f"  WARNING: could not write PID file: {e}", file=sys.stderr)


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
    if s.startswith(("https://", "http://")):
        return True
    if s.endswith(".git"):
        return True
    return bool(re.match(r"^[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+[:/]", s))


def _parse_git_url(raw: str) -> tuple[str, str]:
    """Parse a git URL with optional @ref. Returns (clone_url, ref).

    Only https:// URLs are accepted; ssh:// and git@ scp-style URLs are
    rejected to avoid arbitrary-subprocess/SSRF exposure.
    """
    if raw.startswith(("git@", "ssh://")):
        raise ValueError(
            "Only https:// git URLs are supported (ssh:// and git@ URLs are disabled for security)."
        )
    ref = "HEAD"
    url = raw
    if "@" in raw:
        parts = raw.rsplit("@", 1)
        if not parts[0].startswith(("https://", "http://")):
            if "/" not in parts[1]:
                url, ref = parts
            else:
                url = raw
        else:
            if "/" not in parts[1] and "." not in parts[1]:
                url, ref = parts
    if not url.startswith(("https://", "http://")):
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
        print("  No bundle found — generating (this may take a while)...")
        try:
            result = subprocess.run(
                ["okf", "generate", str(directory), str(bundle_sub)],
                capture_output=True, text=True, timeout=600,
            )
            if result.returncode != 0:
                print("  WARNING: okf generate failed:", file=sys.stderr)
                for line in result.stderr.splitlines()[-5:]:
                    print(f"    {line}")
                print("  Serving source tree instead.")
                return None
            print(f"  Bundle generated → {bundle_sub}")
            return bundle_sub
        except FileNotFoundError:
            print("  WARNING: 'okf' not found on PATH. Cannot generate bundle.")
            print(f"  Run 'okf generate {directory} {bundle_sub}' manually.")
            return None
        except subprocess.TimeoutExpired:
            print("  ERROR: generation timed out (10 min limit).")
            print(f"  Run 'okf generate {directory} {bundle_sub}' manually.")
            return None
    return None


class VizzHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "OKF/" + __version__

    def _authorized(self) -> bool:
        token = getattr(self.server, "auth_token", None)
        if not token:
            return True
        # Accept ?token= query param or Authorization: Bearer <token>
        from urllib.parse import parse_qs, urlparse
        if parse_qs(urlparse(self.path).query).get("token", [""])[0] == token:
            return True
        auth = self.headers.get("Authorization", "")
        return auth.startswith("Bearer ") and auth[7:] == token

    def do_GET(self):
        if not self._authorized():
            self.send_error(401, "Unauthorized")
            return
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
    parser.add_argument("--allow-remote", action="store_true",
                        help="Allow binding to a non-loopback host (requires --token)")
    parser.add_argument("--token", default=None,
                        help="Require this token (via ?token= or Authorization: Bearer) for all requests")
    parser.add_argument("--open", "-o", action="store_true", help="Open browser automatically")
    parser.add_argument("--stop", action="store_true", help="Stop a running server")
    parser.add_argument("--update", action="store_true", help="Fetch latest from git remote before serving")
    parser.add_argument("--generate", action="store_true", help="Run okf generate if bundle missing (first clone only)")
    args = parser.parse_args()

    if args.stop:
        stop_server()
        sys.exit(0)

    if not _is_loopback(args.host) and not args.allow_remote:
        print(
            f"ERROR: refusing to bind to non-loopback host {args.host!r} "
            "without --allow-remote (remote exposure is a security risk).",
            file=sys.stderr,
        )
        sys.exit(1)

    if not _is_loopback(args.host) and not args.token:
        print(
            "ERROR: binding to a non-loopback host requires --token <secret> "
            "so the server is not publicly readable.",
            file=sys.stderr,
        )
        sys.exit(1)

    stop_server(silent=True)

    # Resolve directory — may be a git URL
    raw = args.bundle_dir
    if _is_git_url(raw):
        try:
            url, ref = _parse_git_url(raw)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
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
    if args.token:
        print("  Token auth enabled (send ?token=<token> or Authorization: Bearer <token>).")

    class _Server(socketserver.TCPServer):
        auth_token = args.token

    try:
        with _Server((args.host, args.port), VizzHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        PID_FILE.unlink(missing_ok=True)
        sys.exit(0)
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
