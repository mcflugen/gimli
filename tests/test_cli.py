from io import StringIO

import numpy as np
import pytest
from click.testing import CliRunner
from numpy.testing import assert_array_almost_equal

from gimli import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.gimli, ["--help"])
    assert result.exit_code == 0
    assert result.stdout.startswith("Usage: gimli")

    result = runner.invoke(cli.gimli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.stdout


def test_no_op():
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.gimli)
    assert result.exit_code == 0
    assert result.stdout == ""


@pytest.mark.parametrize("shape", [(-1,), (-1, 1), (3, -1)])
def test_from_file(tmpdir, shape):
    values = np.arange(12.0).reshape(shape)
    with tmpdir.as_cwd():
        runner = CliRunner(mix_stderr=False)

        np.savetxt("values.txt", values, delimiter=",")

        result = runner.invoke(cli.gimli, ["values.txt"])
        data = np.loadtxt(StringIO(result.stdout), delimiter=",")

        assert result.exit_code == 0
        assert_array_almost_equal(np.squeeze(values), np.squeeze(data))


def test_opt_data(tmpdir):
    values = "1,2,3,4,5"
    with tmpdir.as_cwd():
        runner = CliRunner(mix_stderr=False)

        result = runner.invoke(cli.gimli, [f"--data={values}"])
        data = np.loadtxt(StringIO(result.stdout), delimiter=",")

        assert result.exit_code == 0, result.stderr
        assert_array_almost_equal(data, [1, 2, 3, 4, 5])
