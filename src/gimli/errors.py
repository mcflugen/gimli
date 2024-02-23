from __future__ import annotations

from gimli._constants import STATUS_MESSAGE
from gimli._constants import UnitStatus


class GimliError(Exception):
    pass


class IncompatibleUnitsError(GimliError):
    def __init__(self, src: str, dst: str):
        self._src = src
        self._dst = dst

    def __str__(self) -> str:
        return f"incompatible units ({self._src!r}, {self._dst!r})"


class UnitError(GimliError):
    def __init__(self, code: UnitStatus, msg: str | None = None):
        self._code = code
        self._msg = msg or STATUS_MESSAGE.get(self._code, "Unknown")

    def __str__(self) -> str:
        return f"{self._msg} (status {self._code})"


class UnitNameError(UnitError):
    def __init__(self, name: str, code: UnitStatus):
        self._name = name
        self._code = code
        self._msg = STATUS_MESSAGE.get(self._code, "Unknown")

    def __str__(self) -> str:
        return f"{self._name!r}: {self._msg} (status {self._code})"


class DatabaseNotFoundError(GimliError):
    def __init__(self, path: str, status: int):
        self._path = str(path)
        self._status = status

    def __str__(self) -> str:
        return (
            f"{self._path}: unable to locate units database"
            f" ({self._status}): path does not exist"
        )
