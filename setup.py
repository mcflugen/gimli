import os
import sys

import numpy
from setuptools import Extension
from setuptools import setup

udunits2_prefix = os.environ.get("WITH_UDUNITS2", sys.prefix)
if sys.platform.startswith("win"):
    udunits2_prefix = os.path.join(sys.prefix, "Library")

udunits2_libdir = os.environ.get(
    "WITH_UDUNITS2_LIBDIR", os.path.join(sys.prefix, "lib")
)
udunits2_incdir = os.environ.get(
    "WITH_UDUNITS2_INCDIR", os.path.join(sys.prefix, "include")
)

setup(
    include_package_data=True,
    ext_modules=[
        Extension(
            "gimli._udunits2",
            ["src/gimli/_udunits2.pyx"],
            libraries=["udunits2"],
            include_dirs=[numpy.get_include()],
            # include_dirs=[udunits2_incdir, numpy.get_include()],
            library_dirs=[
                os.path.join(os.path.dirname(__file__), "src", "gimli"), udunits2_libdir
            ],
        )
    ],
)
