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
        "-v",
        "--verbose",
        action="store_true",
        help="Also emit status messages to stderr.",
    )
    parser.add_argument("file", type=argparse.FileType("rb"), nargs="*")
    parser.add_argument("-t", "--to", action=Units, metavar="UNIT", default="1")
    parser.add_argument(
        "-f", "--from", dest="from_", metavar="UNIT", action=Units, default="1"
    )

    args = parser.parse_args(argv)

    load = partial(np.loadtxt, delimiter=",")
    dump = partial(np.savetxt, sys.stdout, delimiter=", ", fmt="%f")

    try:
        src_to_dst = args.from_.to(args.to)
    except IncompatibleUnitsError:
        err(f"incompatible units: {args.from_!s}, {args.to!s}")
        return 1

    out(f"Convering {args.from_!s} -> {args.to!s}")
    out(f"1.0 -> {src_to_dst(1.0)}")

    for name in args.file:
        array = load(name)
        dump(np.atleast_1d(src_to_dst(array, out=array)))

    return 0


class Units(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        if not isinstance(values, str):
            parser.error(f"{values!r}: invalid unit string: not a string")

        try:
            units = system.Unit(values)
        except UnitNameError:
            parser.error(f"unknown or poorly-formed unit: {values!r}")
        else:
            setattr(namespace, self.dest, units)
