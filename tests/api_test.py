import pytest
from numpy.testing import assert_almost_equal

from gimli._api import UnitConverter
from gimli._api import convert_units
from gimli._api import get_unit_system
from gimli._system import UnitSystem


def _setup_fake_database(path):
    (path / "udunits2-fake.xml").write_text(
        """\
<?xml version="1.0" encoding="US-ASCII"?>
<unit-system><import>udunits2-base.xml</import></unit-system>""",
        encoding="utf-8",
    )
    (path / "udunits2-base.xml").write_text(
        """\
<?xml version="1.0" encoding="US-ASCII"?>
<unit-system>
    <unit>
        <base/>
        <name><singular>meter</singular></name>
        <symbol>m</symbol>
    </unit>
    <unit>
        <base/>
        <name><singular>kilogram</singular></name>
        <symbol>kg</symbol>
    </unit>
</unit-system>""",
        encoding="utf-8",
    )
    return str(path / "udunits2-fake.xml")


def test_convert_units():
    expected = 0.01
    actual = convert_units(10.0, "m", "km")
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "unit_a, unit_b",
    (("m", "km"), ("km", "m"), ("nm", "parsec"), ("degC", "degF"), ("degK", "degC")),
)
def test_convert_repr(unit_a, unit_b):
    converter_a = UnitConverter(unit_a, unit_b)
    converter_b = eval(repr(converter_a))

    assert converter_a(53.0) == pytest.approx(converter_b(53.0))


@pytest.mark.parametrize("value", (53.0, 0.0, -1.0, [4, 6]))
def test_convert_round_trip(value):
    assert convert_units(convert_units(value, "km", "m"), "m", "km") == pytest.approx(
        value
    )


def test_converter():
    c = UnitConverter("m", "km")
    assert c(10.0) == pytest.approx(0.01)


@pytest.mark.parametrize("value", (53.0, 0.0, -1.0, [4, 6]))
@pytest.mark.parametrize(
    "unit_a, unit_b",
    (("m", "km"), ("km", "m"), ("nm", "parsec"), ("degC", "degF"), ("degK", "degC")),
)
def test_converter_round_trip(value, unit_a, unit_b):
    m_to_km = UnitConverter(unit_a, unit_b)
    km_to_m = UnitConverter(unit_b, unit_a)
    assert_almost_equal(km_to_m(m_to_km(value)), value)


@pytest.mark.parametrize("value", (53.0, 0.0, -1.0, [4, 6]))
@pytest.mark.parametrize(
    "unit_a, unit_b",
    (("m", "km"), ("km", "m"), ("nm", "parsec"), ("degC", "degF"), ("degK", "degC")),
)
def test_converter_inverse(value, unit_a, unit_b):
    m_to_km = UnitConverter(unit_a, unit_b)
    km_to_m = m_to_km.inverse()
    assert_almost_equal(km_to_m(m_to_km(value)), value)


def test_converter_with_default_unit_system():
    m_to_km = UnitConverter("m", "km", system=UnitSystem())
    assert m_to_km(1000.0) == pytest.approx(1.0)


def test_get_unit_system():
    unit_system = get_unit_system()
    assert "m" in unit_system


def test_get_unit_system_singleton():
    system_a = get_unit_system()
    system_b = get_unit_system()
    assert system_a is system_b


def test_converter_with_unit_system(tmp_path):
    system = UnitSystem(_setup_fake_database(tmp_path))

    converter_a = UnitConverter("m / kg", "kg / m", system=system)
    assert converter_a(53) == pytest.approx(1 / 53)
    assert (
        repr(converter_a)
        == f"UnitConverter('m / kg', 'kg / m', system=UnitSystem({system.database!r}))"
    )

    converter_b = eval(repr(converter_a))

    assert converter_a(-2) == pytest.approx(converter_b(-2))
