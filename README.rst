gimli.units
===========

|Black|

|Flake8|

|Test|

|PyPI version|

An object-oriented Python interface to
`udunits2 <https://www.unidata.ucar.edu/software/udunits/>`__ built
with cython.

Requirements
------------

*gimli.units* requires Python 3 and *udunits2*.

Apart from Python, *gimli* has a number of other requirements, the main
one being *udunits2*. *udunits2* is the unit conversion C library that
*gimli* wraps using *cython*. The easiest way to install *udunits2* is
through Anaconda (see the Install section), or *yum* (as *udunits2-devel*
on ubuntu-based Linux). It can, however, also be compiled and installed from source. You can get the source code either as a
`.tar.gz <https://artifacts.unidata.ucar.edu/service/rest/repository/browse/downloads-udunits/>`__
or from `GitHub <https://github.com/Unidata/UDUNITS-2>`__.

All other requirements are available using either *pip* or *conda*. To
see a full listing of the requirements, have a look at the project's
*requirements.txt* file.

If you are a developer of *gimli* you will also want to install
additional dependencies for running *gimli*'s tests to make sure that
things are working as they should. These dependencies are listed in
*requirements-testing.txt*.

Installation
------------

To install *gimli*, first create a new environment in which *gimli* will
be installed. This, although not necessary, will isolate the
installation so that there won't be conflicts with your base *Python*
installation. This can be done with *conda* as:

::

    $ conda create -n gimli python=3
    $ conda activate gimli

Stable Release
--------------

*gimli*, and its dependencies, can be installed either with *pip* or
*conda*. Using *pip*:

::

    $ pip install gimli.units

Using *conda*:

::

    $ conda install gimli.units -c conda-forge

From Source
~~~~~~~~~~~

After downloading the *gimli* source code, run the following from
*gimli*'s top-level folder (the one that contains *setup.py*) to install
*gimli* into the current environment:

::

    $ pip install -e .

Usage
-----

Primarily, *gimli.units* is a Python library with an API that reflects that of
the *udunits2* library. *gimli*, however, also comes with a
command-line interface.

API
===

You primarily will access *gimli* through *gimli.units*,

.. code:: python

    >>> from gimli import units

*units* is an instance of the default *UnitSystem* class, which contains
all of the units contained in a given unit system. If you like, you can create
your own unit system but, typically, the default should be fine.

To get a specific unit from the system, do so by passing a unit
string to the *Units* class. For example,

.. code:: python

    >>> units.Unit("m")
    Unit('meter')
    >>> units.Unit("m/s")
    Unit('meter-second^-1')
    >>> units.Unit("kg m-3")
    Unit('meter^-3-kilogram')
    >>> units.Unit("N m")
    Unit('joule')

Every *Unit* instance has a *to* method, which returns a unit converter
for converting values from one unit to another,

.. code:: python

    >>> lbs = units.Unit("lb")
    >>> kgs = units.Unit("kg")
    >>> kgs_to_lbs = kgs.to(lbs)
    >>> kgs_to_lbs(1.0)
    2.2046226218487757

You can also construct units that are a combination of other units.

.. code:: python

    >>> ft_per_s = units.Unit("ft / s")
    >>> m_per_s = units.Unit("m s-1")
    >>> ft_per_s.to(m_per_s)([1.0, 2.0])
    array([0.3048, 0.6096])

Command-line interface
----------------------

From the command line you can use *gimli* to convert values from one
unit to another.

.. code:: bash

    $ gimli --from=miles --to=ft --data=1.0
    5280.000000

Values to convert are passed through the *--data* option as a
comma-separated list of numbers. You can also provide values through
files and use a dash for *stdin*.

.. code:: bash

    $ echo "1.0" | gimli --from=cal --to=joule -
    4.186800

When reading from a file, *gimli* tries to preserve the format of the
input file,

.. code:: bash

    $ cat values.csv
    1.0, 2.0, 3.0
    4.0, 5.0, 6.0
    $ gimli --from=knot --to=m/s values.txt
    0.514444, 1.028889, 1.543333
    2.057778, 2.572222, 3.086667

.. |Black| image:: https://github.com/mcflugen/gimli/actions/workflows/black.yml/badge.svg
   :target: https://github.com/mcflugen/gimli/actions/workflows/black.yml
.. |Flake8| image:: https://github.com/mcflugen/gimli/actions/workflows/flake8.yml/badge.svg
   :target: https://github.com/mcflugen/gimli/actions/workflows/flake8.yml
.. |Test| image:: https://github.com/mcflugen/gimli/actions/workflows/test.yml/badge.svg
   :target: https://github.com/mcflugen/gimli/actions/workflows/test.yml
.. |PyPI version| image:: https://badge.fury.io/py/gimli.units.svg
   :target: https://badge.fury.io/py/gimli.units
