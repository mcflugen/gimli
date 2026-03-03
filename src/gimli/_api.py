from __future__ import annotations

import os

import numpy as np
from numpy.typing import ArrayLike
from numpy.typing import NDArray

from gimli._system import UnitSystem
from gimli._utils import get_xml_path

_UNIT_SYSTEM_CACHE: dict[str, UnitSystem] = {}


class UnitConverter:
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
    converter: UnitConverter
        A callable object that converts values from *src* to *dst*.

    Examples
    --------
    >>> convert = UnitConverter("degC", "K")
    >>> convert(0.0)
    273.15

    >>> convert = UnitConverter("miles / hr", "km / hour")
    >>> convert(55)
    88.51392
    """

    def __init__(self, src: str, dst: str, system: UnitSystem | None = None) -> None:
        self._system = get_unit_system() if system is None else system

        self._src_to_dst = self._system.Unit(src).to(self._system.Unit(dst))

        self._src = src
        self._dst = dst

    @property
    def source(self) -> str:
        return self._src

    @property
    def destination(self) -> str:
        return self._dst

    def __call__(self, values: ArrayLike) -> float | NDArray[np.floating]:
        if np.isscalar(values):
            return self._src_to_dst(values)
        return self._src_to_dst(np.asarray(values))

    def __repr__(self) -> str:
        args = [repr(self.source), repr(self.destination)]
        if self._system != get_unit_system():
            args += [f"system=UnitSystem({self._system.database!r})"]
        return f"UnitConverter({', '.join(args)})"

    def inverse(self) -> UnitConverter:
        """Create a converter that goes in the opposite direction.

        Examples
        --------
        >>> a = UnitConverter("min / mile", "s / (400 m)")
        >>> int(a(4.0))
        59

        >>> a = UnitConverter("mile", "m")
        >>> a(4.0)
        6437.376
        >>> a.inverse()
        UnitConverter('m', 'mile')

        >>> b = a.inverse()
        >>> b(a(4.0))
        4.0
        """
        return UnitConverter(self.destination, self.source, system=self._system)


def convert_units(
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

    >>> convert_units(10.0, "m", "ft")
    32.80839895013123

    Convert an array:

    >>> convert_units([0.0, 1000.0], "m", "km")
    array([0., 1.])
    """
    converter = UnitConverter(from_, to, system=system)
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


def _canonicalize_path(path: str) -> str:
    return os.path.normcase(os.path.abspath(os.path.normpath(path)))


units = get_unit_system()
