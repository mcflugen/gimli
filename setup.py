import os
import pathlib
import sys

import numpy
from setuptools import Extension
from setuptools import setup

is_windows = sys.platform.startswith("win")
is_macos = sys.platform == "darwin"
is_linux = sys.platform.startswith("linux")

if is_windows:
    lib_ext = ".lib"
    static_libs = (f"udunits2{lib_ext}", f"libexpat{lib_ext}")
else:
    lib_ext = ".a"
    static_libs = (f"libudunits2{lib_ext}", f"libexpat{lib_ext}")

include_dirs = [numpy.get_include()]
library_dirs = []
libraries = []
extra_objects = []
extra_compile_args = []

udunits2_prefix = os.environ.get("UDUNITS2_PREFIX")

if udunits2_prefix is not None:
    udunits2_prefix = pathlib.Path(udunits2_prefix)

    libdir = udunits2_prefix / "lib"
    incdir = udunits2_prefix / "include"

    extra_objects += [
        str(libdir / lib) for lib in static_libs if (libdir / lib).is_file()
    ]

    library_dirs += [str(libdir)] if libdir.is_dir() else []
    include_dirs += [str(incdir)] if incdir.is_dir() else []
else:
    libraries += ["udunits2", "expat"]

setup(
    include_package_data=True,
    ext_modules=[
        Extension(
            "gimli._udunits2",
            ["src/gimli/_udunits2.pyx"],
            libraries=libraries,
            extra_objects=extra_objects,
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            extra_compile_args=extra_compile_args,
        )
    ],
)
