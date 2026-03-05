# Changelog for gimli

## 0.4.0

### Features

- Added new API functions: `convert`, `make_converter`, and `get_unit_system`.
- Added a new `UnitConverter` class that replaces `make_converter` and fixes an
  issue with non-affine transformations.
- Implemented `__hash__` for `Units`.
- Implemented `__richcmp__` in *Cython* to support rich comparisons for `Units`.
- Added `nogil` blocks to the unit converters for improved performance when
  converting large arrays.
- Added new *gimli* exceptions that map *UDUNITS* status codes.
- Added tests for Python 3.10, 3.11, 3.12, 3.13, and 3.14 on the latest versions
  of *Linux*, *macOS*, and *Windows*.

### Changes

- Renamed `gimli.convert` to `gimli.convert_units`.
- Changed the error raised when converting between incompatible units to
  `IncompatibleUnitsError`.
- Set the *UDUNITS* error message handler to suppress error messages.
- Increased the minimum supported Python version to 3.11.

### Fixes

- Fixed `cibuildwheel` builds for *macOS* `x86_64`.
- Fixed failing tests caused by double-import *NumPy* errors by running
  *coverage* directly instead of *pytest-cov*.
- Fixed an issue that caused all CI tests to run under the same Python version.
- Fixed a bug in the unit formatter error string for invalid encoding values.
- Added `NULL` checks to prevent possible segmentation faults.

### Maintenance

- Added a *coverage* session to the *nox* file that runs coverage on an editable
  install rather than on a wheel.
- Replaced *Coveralls* with *Codecov* in CI.
- Updated CI to publish to PyPI/TestPyPI when the workflow is manually
  triggered instead of detecting tags.
- Linked against static libraries when building wheels.
- Removed deprecated `argparse.FileType` usage from the CLI.
- Added a `CONTRIBUTING` document and pull request templates.
- Added the canonical *gimli* version to `pyproject.toml` and use
  `importlib.metadata` in `_version.py` to determine the package version.

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
