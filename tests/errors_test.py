import pytest

from gimli._constants import UnitStatus
from gimli.errors import _STATUS_TO_ERROR
from gimli.errors import GimliError
from gimli.errors import GimliInternalError
from gimli.errors import exception_from_status


def test_status_to_error():
    exc = exception_from_status(UnitStatus.PARSE)
    assert isinstance(exc, GimliError)


def test_status_to_error_bad_status():
    with pytest.raises(GimliError):
        exception_from_status(100)


@pytest.mark.parametrize("fallback", (UnitStatus.PARSE, UnitStatus.OS))
def test_status_to_error_status_is_success(fallback):
    with pytest.raises(_STATUS_TO_ERROR[fallback]):
        raise exception_from_status(UnitStatus.SUCCESS, fallback=fallback)


def test_status_to_error_status_is_success_no_fallback():
    with pytest.raises(GimliInternalError):
        raise exception_from_status(UnitStatus.SUCCESS)
