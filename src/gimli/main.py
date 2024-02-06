import argparse
import sys
from collections.abc import Sequence
from functools import partial
from typing import Any

import numpy as np

from gimli._udunits2 import IncompatibleUnitsError
from gimli._udunits2 import UnitNameError
from gimli._udunits2 import UnitSystem
from gimli._version import __version__
from gimli.utils import err
from gimli.utils import out

system = UnitSystem()
load_values = partial(np.loadtxt, delimiter=",")
dump_values = partial(np.savetxt, sys.stdout, delimiter=", ", fmt="%g")


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

    args = parser.parse_args(argv)

    try:
        src_to_dst = args.from_.to(args.to)
    except IncompatibleUnitsError:
        err(f"[error] incompatible units: {args.from_!s}, {args.to!s}")
        return 1

    if not args.quiet:
        out(f"[info] Convering {args.from_!s} -> {args.to!s}")
        out(f"[info] 1.0 -> {src_to_dst(1.0)}")

    for name in args.file:
        if args.verbose and not args.quiet:
            out(f"[info] reading {name.name}")
        array = load_values(name)
        dump_values(np.atleast_1d(src_to_dst(array, out=array)))

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
