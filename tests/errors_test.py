import pytest

from gimli._constants import UnitStatus
from gimli.errors import GimliError
from gimli.errors import status_to_error


def test_status_to_error():
    exc = status_to_error(UnitStatus.PARSE)
    assert isinstance(exc, GimliError)


def test_status_to_error_bad_status():
    with pytest.raises(GimliError):
        status_to_error(100)


def test_status_to_error_status_is_success():
    with pytest.raises(ValueError):
        status_to_error(UnitStatus.SUCCESS)
