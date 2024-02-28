[anaconda-badge]: https://anaconda.org/conda-forge/gimli.units/badges/version.svg
[anaconda-link]: https://anaconda.org/conda-forge/gimli.units
[build-badge]: https://github.com/mcflugen/gimli/actions/workflows/test.yml/badge.svg
[build-link]: https://github.com/mcflugen/gimli/actions/workflows/test.yml
[expat-github]: https://github.com/libexpat/libexpat
[expat-license]: https://github.com/libexpat/libexpat?tab=MIT-1-ov-file#readme
[pypi-badge]: https://badge.fury.io/py/gimli.units.svg
[pypi-link]: https://badge.fury.io/py/gimli.units
[udunits-download]: https://artifacts.unidata.ucar.edu/service/rest/repository/browse/downloads-udunits/
[udunits-github]: https://github.com/Unidata/UDUNITS-2
[udunits-license]: https://github.com/Unidata/UDUNITS-2/tree/master?tab=License-1-ov-file
[udunits-link]: https://www.unidata.ucar.edu/software/udunits/

![[Build Status][build-link]][build-badge]
![[PyPI][pypi-link]][pypi-badge]
![[Anaconda][anaconda-link]][anaconda-badge]


# gimli.units

An object-oriented Python interface to [udunits2][udunits-link] built with cython.

**NOTE: *gimli.units* includes a vendored version of *udunits2* so that you do not
have to install the *udunits2* library separately.**

## Installation

```
pip install gimli.units
```
or
```
conda install gimli.units -c conda-forge
```

### From Source

```
pip install git+https://github.com/mcflugen/gimli.git
```

Note: `gimli.units` requires the `libudunits` library. You will need to
have this installed before building `gimli.units`. You can do this
using `conda`,

```
conda install udunits2 -c conda-forge
```

or by building `udunits2` from source (we use a
[vendored version](#notice-of-vendored-libraries) of `udunits2`,
which can be found in the `extern` folder of this repository).

## Usage

Primarily, *gimli.units* is a Python module with an [API](#API) that reflects that of
the *udunits2* library. *gimli*, however, also comes with a
[command-line interface](#command-line-interface).

# API

You primarily will access *gimli* through *gimli.units*,

```python
>>> from gimli.units import units
```

*units* is an instance of the default *UnitSystem* class, which contains
all of the units contained in a given unit system. If you like, you can create
your own unit system but, typically, the default should be fine.

*units* is a *dict*-like object whose keys are strings representing units
and values are instances of those units. For example,

```python
>>> units["m"]
Unit('meter')
>>> units["m/s"]
Unit('meter-second^-1')
>>> units["kg m-3"]
Unit('meter^-3-kilogram')
>>> units["N m"]
Unit('joule')
```

Every *Unit* instance has a *to* method, which returns a unit converter
for converting values from one unit to another,

```python
>>> lbs = units["lb"]
>>> kgs = units["kg"]
>>> kgs_to_lbs = kgs.to(lbs)
>>> kgs_to_lbs(1.0)
2.2046226218487757
```

You can also construct units that are a combination of other units.

```python
>>> ft_per_s = units["ft / s"]
>>> m_per_s = units["m s-1"]
>>> ft_per_s.to(m_per_s)([1.0, 2.0])
array([0.3048, 0.6096])
```

## Command-line interface

From the command line you can use *gimli* to convert values from one
unit to another.

```bash
gimli --from=miles --to=ft
```
```
5280.000000
```

Values to convert can be passed through the files (use a dash for *stdin*).

```bash
echo "1.0" | gimli --from=cal --to=joule -
```
```
4.186800
```

When reading from a file, *gimli* tries to preserve the format of the
input file,

```bash
cat values.csv
```
```
1.0, 2.0, 3.0
4.0, 5.0, 6.0
```
```bash
gimli --from=knot --to=m/s values.txt
```
```
0.514444, 1.028889, 1.543333
2.057778, 2.572222, 3.086667
```

## Notice of Vendored Libraries

`gimli.units` includes two third-party libraries, `expat` and `udunits`,
which are "vendored" as part of our codebase. This means that these
libraries are embedded directly within `gimli.units`, rather than being
external dependencies.

### Reasons for Vendoring

- **`udunits`**: A library for units of physical quantities, vendored
  to provide robust unit conversion and management, ensuring compatibility
  and consistency in unit operations.
- **`expat`**: An XML parser library written in C, vendored to ensure
  consistent and reliable XML parsing across various platforms and
  environments without requiring separate installation of the library.
  `expat` is a dependency of `udunits`.

### Implications for Users

- **No Additional Installations**: Users do not need to install these
  libraries separately; they are fully integrated into our package.
- **Package Size**: The inclusion of these libraries increases the size
  of our package. We have taken care to ensure that this does not
  significantly impact the installation and usage experience.
- **Compatibility**: Vendoring these libraries helps us manage
  compatibility and reliability issues, as we use specific versions
  tested to work with our package.

### Licensing

- **`udunits` License**: [License Information for udunits][udunits-license]
- Our use of these vendored libraries complies with their respective
  licenses. Users of our package are also subject to these terms.
- **`expat` License**: [License Information for expat][expat-license]

### Updates and Security

- We actively monitor and incorporate updates, including security patches,
  for these vendored libraries. Should there be any significant updates
  or security concerns, we aim to address these in a timely manner.

### Further Information

- For more information on `udunits`, refer to [udunits' website][udunits-link].
- For more details about `expat`, please visit [expat's website][expat-github].
