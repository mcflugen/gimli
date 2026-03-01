from __future__ import annotations

import os

import numpy as np
from numpy.typing import ArrayLike
from numpy.typing import NDArray

from gimli._system import UnitSystem
from gimli._utils import get_xml_path

_UNIT_SYSTEM_CACHE: dict[str, UnitSystem] = {}


def make_converter(src: str, dst: str, system: UnitSystem | None = None) -> Converter:
    """Create a callable converter between two units.

    Parameters
    ----------
    src: str
        Source unit string (e.g., ``"m"``, ``"Pa"``, ``"degC"``).
    dst: str
        Destination unit string (e.g., ``"km"``, ``"bar"``, ``"K"``).
    system: UnitSystem, optional
        Optional ``UnitSystem`` instance to use. If ``None``, uses the
        cached global unit system returned by ``get_unit_system``.

    Returns
    -------
    converter: Converter
        A callable object that converts values from *src* to *dst*.

    Examples
    --------
    >>> c = make_converter("degC", "K")
    >>> c(0.0)
    273.15
    """
    if system is None:
        _system = get_unit_system()
    else:
        _system = system

    src_units = _system.Unit(src)
    dst_units = _system.Unit(dst)
    src_to_dst = src_units.to(dst_units)

    offset = src_to_dst(0.0)
    scale = src_to_dst(1.0) - offset

    return Converter(src, dst, scale=scale, offset=offset)


def convert(
    values: ArrayLike, from_: str, to: str, system: UnitSystem | None = None
) -> float | NDArray[np.floating]:
    """Convert values from one unit to another.

    This is a convenience wrapper around ``make_converter``. It creates a
    converter and immediately applies it to *values*.

    Parameters
    ----------
    values: array_like
        Scalar or array-like of numeric values to convert.
    from_: str
        Source unit string (e.g., ``"m"``, ``"km"``, ``"degC"``).
    to: str
        Destination unit string (e.g., ``"ft"``, ``"s"``, ``"K"``).
    system: UnitSystem, optional
        Optional :class:`~gimli.UnitSystem` instance to use for parsing and
        conversion. If *None*, uses the cached global unit system returned by
        :func:`get_unit_system`.

    Returns
    -------
    array_like
        Converted values.

    Examples
    --------
    Convert a scalar:

    >>> convert(10.0, "m", "ft")
    32.80839895013123

    Convert an array:

    >>> convert([0.0, 1000.0], "m", "km")
    array([0., 1.])
    """
    converter = make_converter(from_, to, system=system)
    return converter(values)


def get_unit_system(filepath: str | None = None) -> UnitSystem:
    """Get a cached unit system instance.

    This function loads and caches a ``UnitSystem`` keyed by the
    canonical path to the UDUNITS XML database. Repeated calls for the same XML
    path return the same ``UnitSystem`` instance.

    Parameters
    ----------
    filepath: str, optional
        Path used to locate the UDUNITS XML database. If not provided, return
        the default unit system.

    Returns
    -------
    UnitSystem
        The unit system associated with the database path.

    Notes
    -----
    Caching is performed in-process. If you need to isolate unit definitions
    (e.g., for tests), consider constructing a dedicated ``UnitSystem``.

    Examples
    --------
    >>> usys = get_unit_system()
    >>> usys.Unit("m")
    Unit('meter')
    """
    path_to_xml, _ = get_xml_path(filepath)

    canonical_path = _canonicalize_path(path_to_xml)

    if canonical_path not in _UNIT_SYSTEM_CACHE:
        _UNIT_SYSTEM_CACHE[canonical_path] = UnitSystem(canonical_path)
    return _UNIT_SYSTEM_CACHE[canonical_path]


class Converter:
    """Convert units."""

    __slots__ = ("source", "destination", "scale", "offset")

    def __init__(
        self,
        src: str,
        dst: str,
        *,
        scale: float,
        offset: float,
    ) -> None:
        self.source = src
        self.destination = dst
        self.scale = float(scale)
        self.offset = float(offset)

    def __call__(self, values: ArrayLike) -> float | NDArray:
        """Convert values from source to destination units."""
        if np.isscalar(values):
            return self.scale * float(values) + self.offset

        arr = np.asarray(values)
        return arr * self.scale + self.offset

    def __repr__(self) -> str:
        args = (
            repr(self.source),
            repr(self.destination),
            f"scale={self.scale!r}",
            f"offset={self.offset!r}",
        )
        return f"Converter({', '.join(args)})"


def _canonicalize_path(path: str) -> str:
    return os.path.normcase(os.path.abspath(os.path.normpath(path)))


units = get_unit_system()
