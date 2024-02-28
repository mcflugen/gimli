from __future__ import annotations

import os
from collections.abc import Generator
from collections.abc import Mapping

from gimli._udunits2 import Unit
from gimli._udunits2 import _UnitSystem
from gimli._utils import load_database


class UnitSystem(Mapping[str, Unit], _UnitSystem):

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
        self.data: dict[str, Unit] = {}

        for unit in load_database(self.database):
            for symbol in unit["symbol"]:
                self[symbol]

    def __getitem__(self, key: str) -> Unit:
        key = key.strip()

        if key not in self.data:
            unit = self.Unit(key)

            name = unit.name if unit.name is not None else key
            if name not in self.data:
                self.data[name] = unit

            return self.data[name]
        else:
            return self.data[key]

    def __iter__(self) -> Generator[str, None, None]:
        yield from self.data

    def __len__(self) -> int:
        return len(self.data)

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return repr(self.data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnitSystem):
            return NotImplemented
        return os.path.samefile(self.database, other.database)
