"""Legacy import — viz-template.html is now at okf/templates/viz-template.html.
This file kept for backward compat; visualize.py reads the template file directly.
"""
import base64
from pathlib import Path

_TEMPLATE_PATH = Path(__file__).parent / "templates" / "viz-template.html"
DEMO_HTML_B64 = base64.b64encode(_TEMPLATE_PATH.read_bytes()).decode("ascii")
