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

## Requirements

*gimli.units* requires *udunits2*.

*udunits2* is the unit conversion C library that
*gimli* wraps using *cython*. The easiest way to install *udunits2* is
through Anaconda (see the Install section), or *yum* (as *udunits2-devel*
on ubuntu-based Linux). It can, however, also be compiled and installed from source.
You can get the source code either as a [.tar.gz][udunits-download] or from
[GitHub][udunits-github].

All other requirements are available using either *pip* or *conda*. To
see a full listing of the requirements, have a look at the project's
*requirements.in* file.

## Installation

To install *gimli*, first create a new environment in which *gimli* will
be installed. This, although not necessary, will isolate the
installation so that there won't be conflicts with your base *Python*
installation. This can be done with *conda* as:

```
conda create -n gimli python=3
conda activate gimli
```

## Stable Release

*gimli*, and its dependencies, can be installed either with *pip* or
*conda*. Using *pip*:

```
pip install gimli.units
```

Using *conda*:

```
conda install gimli.units -c conda-forge
```

### From Source

After downloading the *gimli* source code, run the following from
*gimli*'s top-level folder (the one that contains *setup.py*) to install
*gimli* into the current environment:

```
pip install -e .
```

## Usage

Primarily, *gimli.units* is a Python library with an API that reflects that of
the *udunits2* library. *gimli*, however, also comes with a
command-line interface.

# API

You primarily will access *gimli* through *gimli.units*,

```python
>>> from gimli import units
```

*units* is an instance of the default *UnitSystem* class, which contains
all of the units contained in a given unit system. If you like, you can create
your own unit system but, typically, the default should be fine.

To get a specific unit from the system, do so by passing a unit
string to the *Units* class. For example,

```python
>>> units.Unit("m")
Unit('meter')
>>> units.Unit("m/s")
Unit('meter-second^-1')
>>> units.Unit("kg m-3")
Unit('meter^-3-kilogram')
>>> units.Unit("N m")
Unit('joule')
```

Every *Unit* instance has a *to* method, which returns a unit converter
for converting values from one unit to another,

```python
>>> lbs = units.Unit("lb")
>>> kgs = units.Unit("kg")
>>> kgs_to_lbs = kgs.to(lbs)
>>> kgs_to_lbs(1.0)
2.2046226218487757
```

You can also construct units that are a combination of other units.

```python
>>> ft_per_s = units.Unit("ft / s")
>>> m_per_s = units.Unit("m s-1")
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

- **`expat`**: An XML parser library written in C, vendored to ensure
  consistent and reliable XML parsing across various platforms and
  environments without requiring separate installation of the library.
  `expat` is a dependency of `udunits`.
- **`udunits`**: A library for units of physical quantities, vendored
  to provide robust unit conversion and management, ensuring compatibility
  and consistency in unit operations.

### Implications for Users

- **No Additional Installations**: Users do not need to install these
  libraries separately; they are fully integrated into our package.
- **Package Size**: The inclusion of these libraries increases the size
  of our package. We have taken care to ensure that this does not
  significantly impact the installation and usage experience.
- **Compatibility**: Vendoring these libraries helps us manage
  compatibility and reliability issues, as we use specific versions
  tested to work seamlessly with our package.

### Licensing

- **`expat` License**: [License Information for expat][expat-license]
- **`udunits` License**: [License Information for udunits][udunits-license]
- Our use of these vendored libraries complies with their respective
  licenses. Users of our package are also subject to these terms.

### Updates and Security

- We actively monitor and incorporate updates, including security patches,
  for these vendored libraries. Should there be any significant updates
  or security concerns, we aim to address these in a timely manner.

### Further Information

- For more details about `expat`, please visit [expat's website][expat-github].
- For more information on `udunits`, refer to [udunits' website][udunits-link].
