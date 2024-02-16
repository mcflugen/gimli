from __future__ import annotations

import contextlib

from gimli._udunits2 import Unit
from gimli._udunits2 import _UnitSystem


class UnitSystem(_UnitSystem):

    """A system of units.

    A unit-system is a set of units that are all defined in terms of
    the same set of base units. In the SI system of units, for example,
    the base units are the meter, kilogram, second, ampere, kelvin,
    mole, and candela. (For definitions of these base units,
    see http://physics.nist.gov/cuu/Units/current.html)

    In the UDUNITS-2 package, every accessible unit belongs to one and
    only one unit-system. It is not possible to convert numeric values
    between units of different unit-systems. Similarly, units belonging
    to different unit-systems always compare unequal.

    Parameters
    ----------
    filepath : str, optional
        Path to a *udunits2* xml-formatted unit database. If not provided,
        a default system of units is used.
    """

    def __init__(self, filepath: str | None = None):
        self._registry: dict[str, Unit] = {}

    def __getitem__(self, key: str) -> Unit:
        with contextlib.suppress(KeyError):
            return self._registry[key]
        self._registry[key] = self.Unit(key)
        return self._registry[key]
