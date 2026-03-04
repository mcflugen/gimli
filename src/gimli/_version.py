from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

try:
    __version__ = version("gimli")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
