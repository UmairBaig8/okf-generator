"""okf serve — launch a local HTTP server for an OKF bundle viz.

Usage:
  okf serve [<bundle_dir>] [options]
  okf serve --stop              Stop a running server
  okf serve --port 8080
"""

import argparse
import http.server
import os
import socketserver
import sys
import webbrowser
from pathlib import Path


PORT = 8000
HOST = "127.0.0.1"
PID_DIR = Path.home() / ".cache" / "okf"
PID_FILE = PID_DIR / "serve.pid"


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


def stop_server():
    pid = read_pid()
    if pid is None:
        print("No running okf serve found.")
        sys.exit(1)
    os.kill(pid, 15)  # SIGTERM
    PID_FILE.unlink(missing_ok=True)
    print(f"Stopped server (PID {pid}).")
    sys.exit(0)


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
    parser.add_argument("bundle_dir", nargs="?", default=".", help="Directory to serve (default: current dir)")
    parser.add_argument("--port", "-p", type=int, default=PORT, help=f"Port (default: {PORT})")
    parser.add_argument("--host", default=HOST, help=f"Host (default: {HOST})")
    parser.add_argument("--open", "-o", action="store_true", help="Open browser automatically")
    parser.add_argument("--stop", action="store_true", help="Stop a running server")
    args = parser.parse_args()

    if args.stop:
        stop_server()

    directory = Path(args.bundle_dir).resolve()
    if not directory.exists():
        print(f"ERROR: Directory not found: {directory}", file=sys.stderr)
        sys.exit(1)

    os.chdir(directory)

    if not os.path.exists("viz.html"):
        print(f"  No viz.html found in {directory}. Run: okf visualize .")
        print(f"  Serving directory listing at http://{args.host}:{args.port}")
    else:
        url = f"http://{args.host}:{args.port}/viz.html"
        print(f"  OKF Viz: {url}")

    write_pid()

    if args.open and os.path.exists("viz.html"):
        webbrowser.open(f"http://{args.host}:{args.port}/viz.html")
    elif args.open:
        webbrowser.open(f"http://{args.host}:{args.port}")

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
