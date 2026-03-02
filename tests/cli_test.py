import contextlib
from io import StringIO

import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

from gimli._main import main


def test_cli_version(capsys):
    with contextlib.suppress(SystemExit):
        assert main(["--version"]) == 0
    output = capsys.readouterr().out

    assert "gimli" in output


def test_command_line_interface(capsys):
    """Test the CLI."""
    with contextlib.suppress(SystemExit):
        assert main(["--help"]) == 0
    assert capsys.readouterr().out.startswith("usage: gimli")


def test_no_op(capsys):
    with contextlib.suppress(SystemExit):
        assert main(["--from=m", "--to=m"]) == 0
    assert capsys.readouterr().out == ""


def test_verbose(tmpdir, capsys):
    values = np.arange(12.0).reshape((3, 4))
    with tmpdir.as_cwd():
        np.savetxt("foobar.txt", values, delimiter=",")
        assert main(["--verbose", "--from=m", "--to=km", "foobar.txt"]) == 0

    last_line = capsys.readouterr().err.strip().splitlines()[-1]
    assert last_line == "[info] reading foobar.txt"


@pytest.mark.parametrize("shape", [(-1,), (-1, 1), (3, -1)])
def test_from_file(tmpdir, shape, capsys):
    values = np.arange(12.0).reshape(shape)
    with tmpdir.as_cwd():
        np.savetxt("values.txt", values, delimiter=",")

        with contextlib.suppress(SystemExit):
            assert (
                main(
                    [
                        *("-f", "m"),
                        *("-t", "m"),
                        "values.txt",
                    ]
                )
                == 0
            )

        data = np.loadtxt(StringIO(capsys.readouterr().out), delimiter=",")
        assert_array_almost_equal(np.squeeze(values), np.squeeze(data))


@pytest.mark.parametrize(
    "values", ["1,2,3,4,5", "2", "3.0", "1e-3", "0.1, 1e2", "-2.3"]
)
def test_opt_to_from(tmpdir, values, capsys):
    with tmpdir.as_cwd():
        with open("values.txt", "w") as fp:
            print(values, file=fp)

        with contextlib.suppress(SystemExit):
            assert (
                main(
                    [
                        *("-f", "m"),
                        *("-t", "km"),
                        "values.txt",
                    ]
                )
                == 0
            )
        actual = np.loadtxt(StringIO(capsys.readouterr().out), delimiter=",")
        expected = np.loadtxt(StringIO(values), delimiter=",") / 1000.0

        assert_array_almost_equal(actual, expected)


def test_opt_to_from_incomaptible(tmpdir, capsys):
    with tmpdir.as_cwd(), contextlib.suppress(SystemExit):
        assert main(["--from=m", "--to=kg"]) != 0


def test_bad_units():
    with contextlib.suppress(SystemExit):
        assert main(["--from=m", "--to=foobar"]) != 0
