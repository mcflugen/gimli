import os
import random

import hypothesis.extra.numpy as hynp
import numpy as np
import pytest
from hypothesis import given
from numpy.testing import assert_allclose
from numpy.testing import assert_array_almost_equal

import gimli
from gimli._constants import UnitFormatting
from gimli._constants import UnitStatus
from gimli._system import UnitSystem
from gimli._utils import get_xml_path
from gimli.errors import DatabaseNotFoundError


@pytest.fixture(scope="module")
def system():
    os.environ.pop("UDUNITS2_XML_PATH", None)
    return UnitSystem()


def test_get_xml():
    os.environ.pop("UDUNITS2_XML_PATH", None)
    path, status = get_xml_path()
    assert os.path.isfile(path)
    assert status == UnitStatus.OPEN_DEFAULT

    path, status = get_xml_path(path)
    assert os.path.isfile(path)
    assert status == UnitStatus.OPEN_ARG

    os.environ["UDUNITS2_XML_PATH"] = str(path)
    path, status = get_xml_path()
    assert os.path.isfile(path)
    assert status == UnitStatus.OPEN_ENV

    with pytest.raises(DatabaseNotFoundError):
        get_xml_path("/path/to/nowhere")


def test_default_system():
    os.environ.pop("UDUNITS2_XML_PATH", None)
    system = UnitSystem()
    assert system.status == "default"
    assert os.path.isfile(system.database)


def test_user_system():
    path = UnitSystem().database
    system = UnitSystem(path)
    assert system.status == "user"
    assert os.path.isfile(system.database)
    assert system == UnitSystem()
    assert UnitSystem(path) == UnitSystem(str(path))


def test_env_system(system):
    os.environ["UDUNITS2_XML_PATH"] = system.database
    env_system = UnitSystem()

    assert env_system.status == "env"
    assert os.path.isfile(env_system.database)
    assert str(env_system) == str(system)
    assert os.path.samefile(system.database, env_system.database)
    assert env_system == system


def test_system_dimensionless(system):
    assert system.dimensionless_unit() == system.Unit("1")
    assert str(system.dimensionless_unit()) == "1"


def test_dimensionless_not_freed_twice():
    system = UnitSystem()
    unit = system.dimensionless_unit()
    del unit
    del system

    system = UnitSystem()
    unit = system.Unit("1")
    del unit
    del system


def test_system_unit_by_name(system):
    assert system.unit_by_name("meter") == system.Unit("m")
    assert system.unit_by_name("meters") == system.Unit("m")
    assert system.unit_by_name("m") is None
    assert system.unit_by_name("meter2") is None
    assert system.unit_by_name("not_a_name") is None


def test_system_unit_by_symbol(system):
    assert system.unit_by_symbol("m") == system.Unit("m")
    assert system.unit_by_symbol("km") is None
    assert system.unit_by_symbol("meter") is None
    assert system.unit_by_symbol("m s-2") is None
    assert system.unit_by_symbol("not_a_symbol") is None


def test_unit_formatting(system):
    unit = system.Unit("0.1 lg(re m/(5 s)^2) @ 50")
    assert (
        unit.format(encoding="ascii", formatting=UnitFormatting.NAMES)
        == "0.1 lg(re 0.04 meter-second^-2) from 50"
    )
    assert (
        unit.format(encoding="ascii", formatting=UnitFormatting.DEFINITIONS)
        == "0.1 lg(re 0.04 m.s-2) @ 50"
    )

    assert (
        unit.format(encoding="iso-8859-1", formatting=UnitFormatting.NAMES)
        == "0.1 lg(re 0.04 meter/second²) from 50"
    )
    assert (
        unit.format(encoding="iso-8859-1", formatting=UnitFormatting.DEFINITIONS)
        == "0.1 lg(re 0.04 m/s²) @ 50"
    )

    assert (
        unit.format(encoding="latin-1", formatting=UnitFormatting.NAMES)
        == "0.1 lg(re 0.04 meter/second²) from 50"
    )
    assert (
        unit.format(encoding="latin-1", formatting=UnitFormatting.DEFINITIONS)
        == "0.1 lg(re 0.04 m/s²) @ 50"
    )

    assert (
        unit.format(encoding="utf-8", formatting=UnitFormatting.NAMES)
        == "0.1 lg(re 0.04 meter·second⁻²) from 50"
    )
    assert (
        unit.format(encoding="utf-8", formatting=UnitFormatting.DEFINITIONS)
        == "0.1 lg(re 0.04 m·s⁻²) @ 50"
    )


@pytest.mark.parametrize(
    ("lhs", "cmp_", "rhs"),
    [
        ("m", "lt", "km"),
        ("m", "le", "km"),
        ("m", "le", "m"),
        ("m", "eq", "m"),
        ("m", "ne", "km"),
        ("km", "ge", "m"),
        ("km", "ge", "km"),
        ("km", "gt", "m"),
    ],
)
def test_unit_comparisons(system, lhs, cmp_, rhs):
    compare = getattr(system.Unit(lhs), f"__{cmp_}__")
    assert compare(system.Unit(rhs))
    with pytest.raises(TypeError):
        compare(rhs)


def test_unit_symbol(system):
    meters = system.Unit("m")
    assert meters.symbol == "m"

    km = system.Unit("km")
    assert km.symbol is None


def test_unit_name(system):
    meters = system.Unit("m")
    assert meters.name == "meter"

    km = system.Unit("km")
    assert km.name is None


def test_unit_is_dimensionless(system):
    assert not system.Unit("m").is_dimensionless
    assert system.Unit("1").is_dimensionless
    assert system.Unit("rad").is_dimensionless


def test_unit_is_convertible(system):
    assert system.Unit("m").is_convertible_to(system.Unit("km"))
    assert not system.Unit("m").is_convertible_to(system.Unit("kg"))

    with pytest.raises(TypeError):
        system.Unit("m").is_convertible_to("km")


def test_unit_converter_length(system):
    meters = system.Unit("m")
    km = system.Unit("km")

    assert meters.to(km)(1.0) == pytest.approx(1e-3)
    with pytest.raises(TypeError):
        meters.to("km")

    m_to_km = meters.to(km)
    assert m_to_km(1.0) == pytest.approx(1e-3)


def test_unit_converter_time(system):
    hours = system.Unit("h")
    seconds = system.Unit("s")
    hours_to_seconds = hours.to(seconds)
    assert hours_to_seconds(1.0) == pytest.approx(3600.0)

    with pytest.raises(TypeError):
        hours.to("s")


def test_unit_converter_same_units(system):
    hours = system.Unit("h")
    hours_to_hours = hours.to(system.Unit("h"))
    assert hours_to_hours(1.0) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("to_", "from_"),
    [("not_a_unit", "m"), ("m", "not_a_unit"), ("not_a_unit", "not_a_unit")],
)
def test_unit_converter_bad_from_units(system, to_, from_):
    with pytest.raises(gimli._udunits2.UdunitsError):
        system[from_].to(system[to_])
        # system.Unit(from_).to(system.Unit(to_))


# @pytest.mark.skip()
def test_unit_converter_incompatible_units(system):
    with pytest.raises(gimli._udunits2.UdunitsError):
        system.Unit("s").to(system.Unit("m"))


def test_unit_converter_inverse(system):
    val = random.random()
    seconds_to_hours = system.Unit("s").to(system.Unit("h"))
    hours_to_seconds = system.Unit("h").to(system.Unit("s"))
    assert hours_to_seconds(seconds_to_hours(val)) == pytest.approx(val)


@pytest.mark.parametrize("dtype", (np.single, np.double))
@pytest.mark.parametrize("shape", [(5,), (5, 1), (4, 5), (5, 6, 7)])
def test_unit_converter_double_array(system, shape, dtype):
    meters = system.Unit("m")
    km = system.Unit("km")

    m_to_km = meters.to(km)
    values_in_m = np.ones(shape, dtype=dtype)
    values_in_km = m_to_km(values_in_m)
    assert_array_almost_equal(values_in_m, values_in_km * 1000.0)
    assert values_in_km.dtype == dtype


@given(
    src_values=hynp.arrays(
        dtype=hynp.floating_dtypes(),
        shape=hynp.array_shapes(),
        elements={"allow_nan": True, "allow_infinity": True},
    ),
)
def test_unit_converter_dtype_array_out_keyword(system, src_values):
    meters = system.Unit("m")
    dam = system.Unit("dam")

    m_to_dam = meters.to(dam)
    values_in_dam = np.empty_like(src_values, dtype=src_values.dtype)
    np.divide(src_values, 10.0, out=src_values)  # ensure that the dtype does not change

    rtn = m_to_dam(src_values, out=values_in_dam)
    assert rtn.dtype == src_values.dtype
    assert rtn.shape == src_values.shape
    assert rtn is values_in_dam

    desired = np.multiply(values_in_dam, 10.0, out=values_in_dam)
    assert_allclose(
        src_values,
        desired,
        equal_nan=True,
        atol=np.finfo(src_values.dtype).resolution,
        rtol=np.finfo(src_values.dtype).resolution,
    )


@given(
    values_in_m=hynp.arrays(
        dtype=hynp.integer_dtypes(),
        shape=hynp.array_shapes(),
    ),
)
def test_unit_converter_from_integer(system, values_in_m):
    meters = system.Unit("m")
    dm = system.Unit("dm")

    m_to_dm = meters.to(dm)

    values_in_dm = m_to_dm(values_in_m)
    assert values_in_dm.dtype == np.double
    assert_array_almost_equal(values_in_m * 10.0, values_in_dm)


@given(
    values=hynp.arrays(
        dtype=hynp.integer_dtypes(),
        shape=hynp.array_shapes(),
    ),
)
def test_unit_converter_to_integer(system, values):
    meters = system.Unit("m")
    dm = system.Unit("dm")

    m_to_dm = meters.to(dm)
    values_in_m = np.ones_like(values, dtype=float)

    with pytest.raises(TypeError):
        m_to_dm(values_in_m, out=values)


@pytest.mark.parametrize("dtype", (np.single, np.double))
def test_unit_converter_in_place(system, dtype):
    meters = system.Unit("m")
    km = system.Unit("km")

    m_to_km = meters.to(km)
    values_in_m = np.ones((10, 5), dtype=dtype)
    rtn = m_to_km(values_in_m, out=values_in_m)
    assert rtn is values_in_m
    assert_array_almost_equal(rtn, 1e-3)


def test_unit_converter_non_contiguous(system):
    meters = system.Unit("m")
    km = system.Unit("km")

    m_to_km = meters.to(km)
    values_in_m = np.ones((10, 5), dtype=float)
    values_in_km = np.empty_like(values_in_m).T
    with pytest.raises(ValueError):
        m_to_km(values_in_m, out=values_in_km)
