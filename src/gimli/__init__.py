from gimli._system import UnitSystem
from gimli._version import __version__

units = UnitSystem()
del UnitSystem

__all__ = ["__version__", "units"]
