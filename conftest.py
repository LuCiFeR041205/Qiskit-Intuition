"""Pytest bootstrap: ensure the repo root is importable so the backend/
and frontend/ packages resolve (e.g. `from backend.core.quantum_engine import ...`)."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
