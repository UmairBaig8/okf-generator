"""OKF — Open Knowledge Format toolkit for codebases.

Generate OKF v0.1 knowledge bundles from source code, look up concepts
for AI agent context injection, and convert bundles into LLM training pairs.

Quick start:
    from okf.generator import scan_codebase, write_bundle
    from okf.lookup import load_bundle, search
    from okf.pairs import process_concept

CLI:
    okf generate ./my_codebase ./okf_bundle
    okf lookup WorldBankConnector
    okf pairs ./okf_bundle ./train.jsonl
    okf summarize ./okf_bundle
"""

__version__ = "0.1.35"
__author__  = "Umair Baig"
__license__ = "MIT"

# Public API surface
from okf.generator import scan_codebase, write_bundle, write_summary, Concept
from okf.lookup    import load_bundle, search

__all__ = [
    "scan_codebase",
    "write_bundle",
    "write_summary",
    "load_bundle",
    "search",
    "Concept",
    "__version__",
]
