#! /usr/bin/env python


class GimliError(Exception):

    pass


class BadUnitError(GimliError):

    def __init__(self, unit):
        self._unit = unit

    def __str__(self):
        return "unknown unit ({0!r})".format(self._unit)


class IncompatibleUnitsError(GimliError):

    def __init__(self, src, dst):
        self._src = src
        self._dst = dst

    def __str__(self):
        return "incompatible units ({0!r}, {1!r})".format(self._src, self._dst)
