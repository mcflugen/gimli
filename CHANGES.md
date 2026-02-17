# Changelog for gimli

## 0.3.4 (unreleased)

- Fixed cibuildwheel builds for *macos* *x86_64*.
- Fixed failing tests by using *coverage* directly instead of *pytest-cov*.
  This fixed tests that failed with double import of *numpy* errors.
- Added tests for Python 3.10, 3.11, 3.12, 3.13, and 3.14 on the latest versions
  of *Linux*, *Mac*, and *Windows*.
- Added `nogil` blocks to the unit converters for speed imrovements for large
  arrays.
- Added `NULL` checks to prevent possible segmentation faults.
- Implemented `__hash__` for `Units`.
- Fixed a bug in the error string for a bad encoding value in the unit formatter.
- Changed error to `IncompatibleUnitsError` when trying to convert between
  units that are not compatible with one another.

## 0.3.3 (2024-10-04)

- Added support for Python 3.13.
- Included vendored versions of both *ununits2* and *expat* so that users don't
  have to install either of those packages separately.

## 0.3.0 (2021-11-16)

- Added support for a wider range of array dtypes (#13)
- Fixed AttributeError when deallocating UnitSystem after exiting Python (#12)
- Fixed --version option for the gimli command (#11)

## 0.2.1 (2021-03-02)

- Fixed a bug caused by passing a single value to the cli (#10)
- Added content to the README, mainly installation and usage instructions (#9)

## 0.2.0b1 (2021-02-22)

- Added release and prerelease actions to publish on PyPI and TestPyPI (#8)
- Change name of package to gimli.units (#7)

## 0.2.0b0 (2021-02-20)

- Added gimli command-line interface (#6)
- Better handling of multi-dimensional and non-contiguous arrays (#5)
- Fixed a issue that caused a segmentation fault when using dimensionless units (#4)

## 0.1.1 (2021-02-17)

- Created the gimli package (#1)
- Set continuous integration using GitHub actions (#2)
- Deploy to TestPyPI on a version tag (#3)
