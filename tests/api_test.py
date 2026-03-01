import pytest
from numpy.testing import assert_almost_equal

from gimli._api import Converter
from gimli._api import convert
from gimli._api import get_unit_system
from gimli._api import make_converter
from gimli._system import UnitSystem


def test_convert():
    expected = 0.01
    actual = convert(10.0, "m", "km")
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "unit_a, unit_b",
    (("m", "km"), ("km", "m"), ("nm", "parsec"), ("degC", "degF"), ("degK", "degC")),
)
def test_convert_repr(unit_a, unit_b):
    converter_a = make_converter(unit_a, unit_b)
    converter_b = eval(repr(converter_a), {"Converter": Converter})

    assert converter_a(53.0) == pytest.approx(converter_b(53.0))


@pytest.mark.parametrize("value", (53.0, 0.0, -1.0, [4, 6]))
def test_convert_round_trip(value):
    assert convert(convert(value, "km", "m"), "m", "km") == pytest.approx(value)


def test_make_converter():
    c = make_converter("m", "km")
    assert c(10.0) == pytest.approx(0.01)


@pytest.mark.parametrize("value", (53.0, 0.0, -1.0, [4, 6]))
@pytest.mark.parametrize(
    "unit_a, unit_b",
    (("m", "km"), ("km", "m"), ("nm", "parsec"), ("degC", "degF"), ("degK", "degC")),
)
def test_make_converter_round_trip(value, unit_a, unit_b):
    m_to_km = make_converter(unit_a, unit_b)
    km_to_m = make_converter(unit_b, unit_a)
    assert_almost_equal(km_to_m(m_to_km(value)), value)


def test_make_converter_with_unit_system():
    m_to_km = make_converter("m", "km", system=UnitSystem())
    assert m_to_km("1000.0") == pytest.approx(1.0)


def test_get_unit_system():
    unit_system = get_unit_system()
    assert "m" in unit_system


def test_get_unit_system_singleton():
    system_a = get_unit_system()
    system_b = get_unit_system()
    assert system_a is system_b
