import contextlib
import os
import sys
from collections.abc import Generator
from functools import partial
from typing import Any
from xml.etree import ElementTree

if sys.version_info >= (3, 12):  # pragma: no cover (PY12+)
    import importlib.resources as importlib_resources
else:  # pragma: no cover (<PY312)
    import importlib_resources

from gimli._constants import UnitStatus
from gimli.errors import DatabaseNotFoundError

out = partial(print, file=sys.stderr)
err = partial(print, file=sys.stderr)


@contextlib.contextmanager
def suppress_stdout() -> Generator[None, None, None]:
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
    # Save the actual stdout (1) and stderr (2) file descriptors.
    save_fds = [os.dup(1), os.dup(2)]

    os.dup2(null_fds[0], 1)
    os.dup2(null_fds[1], 2)

    yield

    # Re-assign the real stdout/stderr back to (1) and (2)
    os.dup2(save_fds[0], 1)
    os.dup2(save_fds[1], 2)
    # Close the null files
    for fd in null_fds + save_fds:
        os.close(fd)


def get_xml_path(filepath: str | None = None) -> tuple[str, UnitStatus]:
    """Get the path to a unit database.

    Parameters
    ----------
    filepath : str, optional
        The path to an xml-formatted unit database. If not provided, use
        the value of the *UDUNITS2_XML_PATH* environment variable,
        otherwise use a default unit database.

    Returns
    -------
    str
        The path to a units database.
    """
    if filepath is None:
        try:
            filepath = os.environ["UDUNITS2_XML_PATH"]
        except KeyError:
            filepath = str(
                importlib_resources.files("gimli") / "data/udunits/udunits2.xml"
            )
            status = UnitStatus.OPEN_DEFAULT
        else:
            status = UnitStatus.OPEN_ENV
    else:
        status = UnitStatus.OPEN_ARG

    if not os.path.isfile(filepath):
        raise DatabaseNotFoundError(filepath, status)

    return filepath, status


def load_database(path: str) -> list[dict[str, Any]]:
    base = os.path.dirname(path)
    root = ElementTree.parse(path).getroot()

    units = []
    for import_path in (child.text for child in root.findall("import")):
        if isinstance(import_path, str):
            units += load_database(os.path.join(base, import_path))

    for child in root.findall("unit"):
        units.append(
            {
                "name": {
                    "singular": child.findtext("name/singular", default=False),
                    "plural": child.findtext("name/plural", default=False),
                },
                "symbol": [symbol.text for symbol in child.findall("symbol")],
                "base": child.find("base") is not None,
                "aliases": [
                    {
                        "name": {
                            "singular": alias.findtext("singular"),
                            "plural": alias.findtext("plural", default=False),
                        }
                    }
                    for alias in child.findall("aliases/name")
                ]
                + [{"symbol": alias.text} for alias in child.findall("aliases/symbol")],
                "def": child.findtext("def", default=False),
            }
        )

    return units
