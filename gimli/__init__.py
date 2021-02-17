import pkg_resources

from ._udunits2 import Unit, UnitEncoding, UnitFormatting, UnitStatus, UnitSystem
from ._udunits2 import UnitNameError
from .errors import BadUnitError, IncompatibleUnitsError

__version__ = pkg_resources.get_distribution("gimli").version
__all__ = ["BadUnitError", "IncompatibleUnitsError", "Unit", "UnitEndoding", "UnitFormatting", "UnitNameError", "UnitStatus", "UnitSystem"]

del pkg_resources
