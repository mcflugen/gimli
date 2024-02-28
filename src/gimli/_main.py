import argparse
import sys
from collections.abc import Sequence
from typing import Any

import numpy as np

from gimli._constants import STATUS_MESSAGE
from gimli._system import UnitSystem
from gimli._udunits2 import UdunitsError
from gimli._utils import err
from gimli._utils import out
from gimli._version import __version__
from gimli.errors import IncompatibleUnitsError
from gimli.errors import UnitNameError

system = UnitSystem()


def main(argv: tuple[str, ...] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gimli")
    parser.add_argument("--version", action="version", version=f"gimli {__version__}")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help=(
            "Don't emit non-error messages to stderr. Errors are still emitted, "
            "silence those with 2>/dev/null."
        ),
    )
    parser.add_argument(
        *("-v", "--verbose"),
        action="store_true",
        help="Also emit status messages to stderr.",
    )
    parser.add_argument("file", type=argparse.FileType("rb"), nargs="*")
    parser.add_argument(
        *("-f", "--from"),
        dest="from_",
        metavar="UNIT",
        action=UnitType,
        default=system.Unit("1"),
        help="Source units.",
    )
    parser.add_argument(
        *("-t", "--to"),
        action=UnitType,
        metavar="UNIT",
        default=system.Unit("1"),
        help="Destination units.",
    )
    parser.add_argument(
        "-o", "--output", type=argparse.FileType("w"), default=sys.stdout
    )

    args = parser.parse_args(argv)

    try:
        src_to_dst = args.from_.to(args.to)
    except IncompatibleUnitsError:
        err(f"[error] incompatible units: {args.from_!s}, {args.to!s}")
        return 1
    except UdunitsError as error:
        err(
            f"[error] udunits internal error (error code {error.code}:"
            f" {STATUS_MESSAGE.get(error.code, 'unknown')})"
        )
        return 1

    if not args.quiet:
        out(f"[info] Convering {args.from_!s} -> {args.to!s}")
        out(f"[info] 1.0 -> {src_to_dst(1.0)}")

    for name in args.file:
        if args.verbose and not args.quiet:
            out(f"[info] reading {name.name}")
        array = np.loadtxt(name, delimiter=",")
        np.savetxt(
            args.output,
            np.atleast_1d(src_to_dst(array, out=array)),
            delimiter=", ",
            fmt="%g",
        )

    return 0


class UnitType(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        if not isinstance(values, str):
            parser.error(f"[error] {values!r}: invalid unit string: not a string")

        try:
            units = system.Unit(values)
        except UnitNameError:
            parser.error(f"[error] unknown or poorly-formed unit: {values!r}")
        else:
            setattr(namespace, self.dest, units)
