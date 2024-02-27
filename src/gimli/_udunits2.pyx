# cython: language_level=3
from __future__ import annotations

import os
import sys

import numpy as np

cimport numpy as np
from libc.stdlib cimport free
from libc.stdlib cimport malloc
from libc.string cimport strcpy

from gimli._constants import UDUNITS_ENCODING
from gimli._constants import UnitEncoding
from gimli._constants import UnitFormatting
from gimli._constants import UnitStatus
from gimli._utils import get_xml_path
from gimli._utils import suppress_stdout
from gimli.errors import IncompatibleUnitsError

DOUBLE = np.double
FLOAT = np.float32

ctypedef np.double_t DOUBLE_t
ctypedef np.float_t FLOAT_t


class UdunitsError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f"udunits error ({self.code})"


cdef extern from "udunits2.h":
    ctypedef struct ut_system:
        pass
    ctypedef struct ut_unit:
        pass
    ctypedef struct cv_converter:
        pass
    ctypedef int ut_encoding;
    ctypedef int ut_status;

    const char* ut_get_path_xml(const char* path, ut_status* status)
    ut_unit* ut_get_unit_by_symbol(const ut_system* system, const char* symbol)
    ut_unit* ut_get_unit_by_name(const ut_system* system, const char* name)

    ut_system* ut_read_xml(const char * path)
    ut_unit* ut_parse(const ut_system* system, const char* string, int encoding)
    ut_unit* ut_get_dimensionless_unit_one(const ut_system* system)
    void ut_free_system(ut_system* system)

    int ut_are_convertible(const ut_unit* unit1, const ut_unit* unit2)
    int ut_format(const ut_unit* unit, char* buf, size_t size, unsigned opts)
    const char* ut_get_name (const ut_unit* unit, ut_encoding encoding)
    const char* ut_get_symbol (const ut_unit* unit, ut_encoding encoding)
    ut_system* ut_get_system(const ut_unit* unit)
    int ut_is_dimensionless(const ut_unit* unit)
    int ut_compare(const ut_unit* unit1, const ut_unit* unit2)
    void ut_free(ut_unit* unit)

    cv_converter* ut_get_converter(ut_unit* const src, ut_unit* const dst)
    double cv_convert_double(const cv_converter* converter, const double value)
    double* cv_convert_doubles(
        const cv_converter* converter, const double* src, size_t count, double* dst
    )
    np.float32_t* cv_convert_floats(
        const cv_converter* converter, const np.float32_t* src, size_t count, np.float32_t* dst
    )
    void cv_free(cv_converter* conv)

    ut_status ut_get_status()


cdef class _UnitSystem:
    cdef ut_system* _unit_system
    cdef ut_status _status
    cdef char* _filepath

    def __cinit__(self, filepath=None):
        cdef char* path

        filepath, self._status = get_xml_path(filepath)
        as_bytes = filepath.encode("utf-8")

        self._filepath = <char*>malloc((len(as_bytes) + 1) * sizeof(char))
        strcpy(self._filepath, as_bytes)

        with suppress_stdout():
            self._unit_system = ut_read_xml(self._filepath)

        if self._unit_system == NULL:
            status = ut_get_status()
            raise UdunitsError(status)

    def dimensionless_unit(self):
        """The dimensionless unit used by the unit system.

        Returns
        -------
        Unit
            The dimensionless unit of the system.
        """
        cdef ut_unit* unit = ut_get_dimensionless_unit_one(self._unit_system)
        if unit == NULL:
            raise UdunitsError(ut_get_status())
        return Unit.from_ptr(unit, owner=False)

    def unit_by_name(self, name):
        """Get a unit from the system by name.

        Parameters
        ----------
        name : str
            Name of a unit.

        Returns
        -------
        Unit or None
            The unit of the system that *name* maps to. If no mapping exists,
            return ``None``.
        """
        unit = ut_get_unit_by_name(self._unit_system, name.encode("utf-8"))
        if unit == NULL:
            status = ut_get_status()
            if status == UnitStatus.SUCCESS:
                return None
            else:
                raise RuntimeError("system and/or name is NULL")
        return Unit.from_ptr(unit, owner=True)

    def unit_by_symbol(self, symbol):
        """Get a unit from the system by symbol.

        Parameters
        ----------
        symbol : str
            Symbol of a unit.

        Returns
        -------
        Unit or None
            The unit of the system that *symbol* maps to. If no mapping exists,
            return ``None``.
        """
        unit = ut_get_unit_by_symbol(self._unit_system, symbol.encode("utf-8"))
        if unit == NULL:
            status = ut_get_status()
            if status == UnitStatus.SUCCESS:
                return None
            else:
                raise RuntimeError("system and/or symbol is NULL")
        return Unit.from_ptr(unit, owner=True)

    def Unit(self, name):
        """Construct a unit from a unit string.

        Parameters
        ----------
        name : str
            Unit string.

        Returns
        -------
        Unit
            A new unit corresponding the the provided string.
        """
        unit = ut_parse(self._unit_system, name.encode("utf-8"), UnitEncoding.UTF8)
        if unit == NULL:
            status = ut_get_status()
            raise UdunitsError(status)
        if ut_is_dimensionless(unit):
            return Unit.from_ptr(unit, owner=False)
        else:
            return Unit.from_ptr(unit, owner=True)


    @property
    def database(self) -> str:
        """Path to the unit-database being used."""
        return self._filepath.decode()

    @property
    def status(self):
        """Status that indicates how the database was found.

        Returns
        -------
        str
            *'user'* if a user-supplied path was used, *'env'* if the path
            was provided by the *UDUNITS2_XML_PATH* environment variable, or
            *'default'* if the default path was used.
        """
        if self._status == UnitStatus.OPEN_ARG:
            return "user"
        elif self._status == UnitStatus.OPEN_ENV:
            return "env"
        elif self._status == UnitStatus.OPEN_DEFAULT:
            return "default"
        else:
            raise RuntimeError("unknown unit_system status")

    def __dealloc__(self):
        ut_free_system(self._unit_system)
        free(self._filepath)
        self._unit_system = NULL
        self._filepath = NULL
        self._status = 0


cdef class Unit:

    cdef ut_unit* _unit
    cdef bint ptr_owner
    cdef char[2048] _buffer

    @staticmethod
    cdef Unit from_ptr(ut_unit* unit_ptr, bint owner=False):
        if unit_ptr == NULL:
            raise RuntimeError("unit pointer is NULL")

        cdef Unit unit = Unit.__new__(Unit)
        unit._unit = unit_ptr
        unit.ptr_owner = owner
        return unit

    def __cinit__(self):
        self.ptr_owner = False

    def to(self, unit):
        """Construct a unit converter to convert another unit.

        Parameters
        ----------
        unit : Unit
            The unit to convert to.

        Returns
        -------
        UnitConverter
            A converter that converts values to the provided unit.
        """
        return self.UnitConverter(unit)

    cpdef UnitConverter(self, Unit unit):
        with suppress_stdout():
            converter = ut_get_converter(self._unit, unit._unit)

        if converter == NULL:
            status = ut_get_status()
            raise UdunitsError(status)
            # raise IncompatibleUnitsError(str(self), str(unit))

        return UnitConverter.from_ptr(converter, owner=True)

    def __dealloc__(self):
        if self._unit is not NULL and self.ptr_owner is True:
            ut_free(self._unit)
            self._unit = NULL
            self.ptr_owner = False


    def __str__(self):
        return self.format(encoding="ascii")

    def __repr__(self):
        return "Unit({0!r})".format(self.format(encoding="ascii"))

    cpdef compare(self, Unit other):
        """Compare units.

        Parameters
        ----------
        other : Unit
            A unit to compare to.

        Returns
        -------
        int
            A negative integer if this unit is less than the provided
            unit, 0 if they are equal, and a positive integer if this
            unit is greater.
        """
        return ut_compare(self._unit, other._unit)

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __eq__(self, other):
        return self.compare(other) == 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ne__(self, other):
        return self.compare(other) != 0

    def format(self, encoding="ascii", formatting=UnitFormatting.NAMES):
        try:
            unit_encoding = UDUNITS_ENCODING[encoding]
        except KeyError:
            raise ValueError("unknown encoding ({encoding})")

        str_len = ut_format(
            self._unit, self._buffer, 2048, opts=unit_encoding | formatting
        )
        if str_len >= 2048:
            raise ValueError("unit string is too large")

        return self._buffer.decode(encoding=encoding)

    @property
    def name(self):
        """Name of the unit.

        Returns
        -------
        str or None
            Name of the unit as a string or, ``None`` if no mapping exists.
        """
        name = ut_get_name(self._unit, 0)
        if name == NULL:
             status = ut_get_status()
             if status == UnitStatus.SUCCESS:
                 return None
             else:
                 raise UdunitsError(status)
        else:
            return name.decode()

    @property
    def symbol(self):
        """Symbol of the unit.

        Returns
        -------
        str or None
            Symbol of the unit as a string or, ``None`` if no mapping exists.
        """
        symbol = ut_get_symbol(self._unit, 0)
        if symbol == NULL:
             status = ut_get_status()
             if status == UnitStatus.SUCCESS:
                 return None
             else:
                 raise UdunitsError(status)
        else:
            return symbol.decode()

    @property
    def is_dimensionless(self):
        """Check if the unit is dimensionless.

        Returns
        -------
        bool
            ``True`` if the unit is dimensionless, otherwise ``False``.
        """
        rtn = ut_is_dimensionless(self._unit)
        if rtn != 0:
            return True
        else:
            status = ut_get_status()
            if status == UnitStatus.SUCCESS:
                return False
            else:
                raise UdunitsError(status)


    cpdef is_convertible_to(self, Unit unit):
        return bool(ut_are_convertible(self._unit, unit._unit))



cpdef as_floating_array(array):
    """Convert an array into a float array that can be passed to udunits functions."""
    if array.dtype not in (np.single, np.double):
        return array.astype(np.double)
    return array


cpdef as_floating_array_like(prototype, out=None):
    """Create a floating array that is like another array with regards to its dtype."""
    if out is None:
        out = np.empty_like(prototype)

    if np.can_cast(prototype.dtype, out.dtype):
        return as_floating_array(out)
    else:
        raise TypeError(f"unable to cast from {prototype.dtype} to {out.dtype}")


cdef class UnitConverter:

    """Convert numeric values between compatible units."""

    cdef cv_converter* _conv
    cdef bint ptr_owner

    @staticmethod
    cdef UnitConverter from_ptr(cv_converter* converter_ptr, bint owner=False):
        cdef UnitConverter converter = UnitConverter.__new__(UnitConverter)
        converter._conv = converter_ptr
        converter.ptr_owner = owner
        return converter

    def __cinit__(self):
        self.ptr_owner = False

    def __call__(self, values, out=None):
        """Convert a value from one unit to another.

        Parameters
        ----------
        value ; number, or array-like
            The value or values to convert.
        out : array-like, optional
            If converting values from an array, the converted values
            will be placed here. To convert in-place, this can be
            the input array of values. If ``None``, a new array
            will be created to hold the converted values.

        Returns
        -------
        value or array-like
            The converted values or values.
        """
        try:
            n_items = len(values)
        except TypeError:
            return self._convert_scalar(values)
        else:
            values_save, out_save = values, out
            values = as_floating_array(np.ascontiguousarray(values))

            out = as_floating_array_like(values_save, out=out)

            if not out.flags["C_CONTIGUOUS"]:
                raise ValueError("out array is not C-contiguous")

            buffer = np.frombuffer(out.data, dtype=out.dtype).reshape(-1)
            values = np.frombuffer(values.data, dtype=values.dtype).reshape(-1)

            if out.dtype == np.double:
                rtn = self._convert_array(values, buffer)
            elif out.dtype == np.single:
                rtn = self._convert_float_array(values, buffer)
            else:
                raise ValueError(f"udunits does not support {out.dtype}")

            if out_save is not None and out is not out_save:
                out_save.flat = rtn.flat
                out = out_save

            return out

    cdef _convert_scalar(self, value):
        return cv_convert_double(self._conv, value)

    cdef _convert_array(
        self,
        np.ndarray[DOUBLE_t, ndim=1] values,
        np.ndarray[DOUBLE_t, ndim=1] out,
    ):
        cv_convert_doubles(self._conv, &values[0], len(values), &out[0])
        return out

    cdef _convert_float_array(
        self,
        np.ndarray[np.float32_t, ndim=1] values,
        np.ndarray[np.float32_t, ndim=1] out,
    ):
        cv_convert_floats(self._conv, &values[0], len(values), &out[0])
        return out

    def __dealloc__(self):
        if self._conv is not NULL and self.ptr_owner is True:
            cv_free(self._conv)
            self._conv = NULL
            self.ptr_owner = False
