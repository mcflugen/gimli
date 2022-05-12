import pathlib
import sys

import pkg_resources
from setuptools import Extension, setup


udunits2_prefix = pathlib.Path(sys.prefix)
if sys.platform.startswith("win"):
    udunits2_prefix = udunits2_prefix / "Library"

numpy_incl = pkg_resources.resource_filename("numpy", "core/include")

# see setup.cfg for static metadata
setup(
    ext_modules=[
        Extension(
            "gimli._udunits2",
            ["gimli/_udunits2.pyx"],
            libraries=["udunits2"],
            include_dirs=[str(udunits2_prefix / "include"), numpy_incl],
            library_dirs=[str(udunits2_prefix / "lib")],
        )
    ],
)
