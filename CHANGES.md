# Changelog for gimli

## 0.3.1 (2024-02-14)

- Added support for Python 3.12 and dropped support for Python less than 3.10 (#16).
- Added vendored versions of `udunits` and `expat` so that users don't have to install
  `libudunits` separately.

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
