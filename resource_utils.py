"""Helpers for loading bundled resources in development and PyInstaller builds."""

import base64
import sys
from functools import lru_cache
from pathlib import Path


def resource_path(filename: str) -> Path:
    """Return the real path of a resource, including inside a one-file executable."""
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return bundle_dir / filename


@lru_cache(maxsize=None)
def image_as_base64(filename: str) -> str:
    """Load an image in a form Flet can render without relying on the current folder."""
    image_path = resource_path(filename)
    try:
        return base64.b64encode(image_path.read_bytes()).decode("ascii")
    except OSError:
        return ""
