#! /usr/bin/env python


class GimliError(Exception):
    pass


class IncompatibleUnitsError(GimliError):
    def __init__(self, src, dst):
        self._src = src
        self._dst = dst

    def __str__(self):
        return f"incompatible units ({self._src!r}, {self._dst!r})"
