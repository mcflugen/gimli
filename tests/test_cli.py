from click.testing import CliRunner

from gimli import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.gimli, ["--help"])
    assert result.exit_code == 0

    result = runner.invoke(cli.gimli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.stdout

    result = runner.invoke(cli.gimli)
    assert result.exit_code == 0
