"""Make codebase modules importable for discovery launched from repo root."""

from pathlib import Path
import sys


CODEBASE_DIR = Path(__file__).resolve().parent.parent
if str(CODEBASE_DIR) not in sys.path:
    sys.path.insert(0, str(CODEBASE_DIR))
