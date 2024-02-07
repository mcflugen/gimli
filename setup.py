import os
import sys

import numpy
from setuptools import Extension
from setuptools import setup


udunits2_prefix = os.environ.get("WITH_UDUNITS2", sys.prefix)
if sys.platform.startswith("win"):
    udunits2_prefix = os.path.join(sys.prefix, "Library")

setup(
    include_package_data=True,
    ext_modules=[
        Extension(
            "gimli._udunits2",
            ["src/gimli/_udunits2.pyx"],
            libraries=["udunits2"],
            include_dirs=[
                os.path.join(udunits2_prefix, "include"),
                numpy.get_include(),
            ],
            library_dirs=[os.path.join(udunits2_prefix, "lib")],
        )
    ],
)
