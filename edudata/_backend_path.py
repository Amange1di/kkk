"""Helpers for loading the Django project from the backend directory."""

from pathlib import Path
import sys


def add_backend_to_path():
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
    backend_path = str(backend_dir)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
