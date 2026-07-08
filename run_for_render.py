"""Uvicorn entrypoint for Render — exposes the OKF dashboard FastAPI app.

Usage on Render:
    uvicorn run_for_render:app --host 0.0.0.0 --port 8000

The bundle path is read from the ``OKF_BUNDLE_DIR`` environment variable
(default: ``./okf_bundle``).
"""

import os
from pathlib import Path

from okf.dashboard import build_app

bundle_dir = Path(os.environ.get("OKF_BUNDLE_DIR", "./okf_bundle"))
app = build_app(bundle_dir)
