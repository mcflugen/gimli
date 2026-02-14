import os
import sys

import numpy
from setuptools import Extension
from setuptools import setup

udunits2_prefix = os.environ.get("UDUNITS2_PREFIX", sys.prefix)
if sys.platform.startswith("win") and "UDUNITS_PREFIX" not in os.environ:
    udunits2_prefix = os.path.join(sys.prefix, "Library")
vendored_prefix = os.path.join(os.path.dirname(__file__), "dist", "extern")

extra_link_args = []
if sys.platform.startswith("linux"):
    extra_link_args.append(f"-Wl,-rpath,{os.path.join(udunits2_prefix, 'lib')}")

setup(
    include_package_data=True,
    ext_modules=[
        Extension(
            "gimli._udunits2",
            ["src/gimli/_udunits2.pyx"],
            libraries=["udunits2"],
            include_dirs=[
                numpy.get_include(),
                os.path.join(udunits2_prefix, "include"),
                os.path.join(vendored_prefix, "include"),
            ],
            library_dirs=[
                os.path.join(udunits2_prefix, "lib"),
                os.path.join(vendored_prefix, "lib"),
            ],
            extra_link_args=extra_link_args,
        )
    ],
)
