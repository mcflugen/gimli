from __future__ import annotations

from enum import IntEnum
from enum import IntFlag


class UnitStatus(IntEnum):
    SUCCESS = 0
    BAD_ARG = 1
    EXISTS = 2
    NO_UNIT = 3
    OS = 4
    NOT_SAME_SYSTEM = 5
    MEANINGLESS = 6
    NO_SECOND = 7
    VISIT_ERROR = 8
    CANT_FORMAT = 9
    SYNTAX = 10
    UNKNOWN = 11
    OPEN_ARG = 12
    OPEN_ENV = 13
    OPEN_DEFAULT = 14
    PARSE = 15


class UnitEncoding(IntEnum):
    ASCII = 0
    ISO_8859_1 = 1
    LATIN1 = 1
    UTF8 = 2


class UnitFormatting(IntFlag):
    NAMES = 4
    DEFINITIONS = 8


STATUS_MESSAGE = {
    UnitStatus.SUCCESS: "Success",
    UnitStatus.BAD_ARG: "An argument violates the function's contract",
    UnitStatus.EXISTS: "Unit, prefix, or identifier already exists",
    UnitStatus.NO_UNIT: "No such unit exists",
    UnitStatus.OS: "Operating-system error.  See 'errno'",
    UnitStatus.NOT_SAME_SYSTEM: "The units belong to different unit-systems",
    UnitStatus.MEANINGLESS: "The operation on the unit(s) is meaningless",
    UnitStatus.NO_SECOND: "The unit-system doesn't have a unit named 'second'",
    UnitStatus.VISIT_ERROR: "An error occurred while visiting a unit",
    UnitStatus.CANT_FORMAT: "A unit can't be formatted in the desired manner",
    UnitStatus.SYNTAX: "string unit representation contains syntax error",
    UnitStatus.UNKNOWN: "string unit representation contains unknown word",
    UnitStatus.OPEN_ARG: "Can't open argument-specified unit database",
    UnitStatus.OPEN_ENV: "Can't open environment-specified unit database",
    UnitStatus.OPEN_DEFAULT: "Can't open installed, default, unit database",
    UnitStatus.PARSE: "Error parsing unit specification",
}


UDUNITS_ENCODING = {
    "ascii": UnitEncoding.ASCII,
    "us-ascii": UnitEncoding.ASCII,
    "iso-8859-1": UnitEncoding.ISO_8859_1,
    "iso8859-1": UnitEncoding.ISO_8859_1,
    "latin-1": UnitEncoding.LATIN1,
    "latin1": UnitEncoding.LATIN1,
    "utf-8": UnitEncoding.UTF8,
    "utf8": UnitEncoding.UTF8,
}
