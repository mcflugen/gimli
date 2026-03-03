from __future__ import annotations

from gimli._constants import STATUS_MESSAGE
from gimli._constants import UnitStatus


def exception_from_status(
    status: UnitStatus,
    message: str | None = None,
    *,
    fallback: UnitStatus | None = None,
) -> GimliError:
    if status == UnitStatus.SUCCESS:
        if fallback is None:
            raise GimliInternalError("status is success but no fallback given")
        status = fallback

    exc_type = _STATUS_TO_ERROR.get(status)
    if exc_type is None:
        raise GimliInternalError(f"unknown udunits status ({status!r})")

    desc = STATUS_MESSAGE[status]
    if message is None:
        return exc_type(f"UDUNITS-2 error: {desc}")
    else:
        exc = exc_type(message)
        exc.add_note(f"UDUNITS-2 status: {status} - {desc}")
        return exc


class GimliError(Exception):
    """Base class for all gimli errors."""


class GimliInternalError(GimliError):
    """Internal invariant/contract violation (likely a gimli bug)."""


class UnitDatabaseError(GimliError):
    """Failure opening/reading/parsing the unit database."""


class DatabaseNotFoundError(UnitDatabaseError):
    """Deprecated. Use UnitDatabaseError instead."""


class UnitSystemError(GimliError):
    """Unit system is inconsistent or incompatible."""


class UnitNotFoundError(GimliError, LookupError):
    """Requested unit/prefix/identifier does not exist."""


class UnitParseError(GimliError, ValueError):
    """Unit string cannot be parsed."""


class UnitNameError(UnitParseError):
    """Deprecated. Use UnitParseError instead."""


class UnitOperationError(GimliError, ValueError):
    """Unit operation is invalid/meaningless (or formatting not possible)."""


class IncompatibleUnitsError(UnitOperationError):
    """Deprecated. Use UnitOperationError instead."""


_STATUS_TO_ERROR: dict[UnitStatus, type[GimliError] | None] = {
    UnitStatus.SUCCESS: None,
    UnitStatus.BAD_ARG: GimliInternalError,
    UnitStatus.EXISTS: UnitSystemError,
    UnitStatus.NO_UNIT: UnitNotFoundError,
    UnitStatus.OS: UnitDatabaseError,
    UnitStatus.NOT_SAME_SYSTEM: UnitSystemError,
    UnitStatus.MEANINGLESS: UnitOperationError,
    UnitStatus.NO_SECOND: UnitSystemError,
    UnitStatus.VISIT_ERROR: GimliInternalError,
    UnitStatus.CANT_FORMAT: UnitOperationError,
    UnitStatus.SYNTAX: UnitParseError,
    UnitStatus.UNKNOWN: UnitParseError,
    UnitStatus.OPEN_ARG: UnitDatabaseError,
    UnitStatus.OPEN_ENV: UnitDatabaseError,
    UnitStatus.OPEN_DEFAULT: UnitDatabaseError,
    UnitStatus.PARSE: UnitParseError,
}
