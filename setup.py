import pathlib
import sys

from setuptools import Extension, find_packages, setup


udunits2_prefix = pathlib.Path(sys.prefix)
if sys.platform.startswith("win"):
    udunits2_prefix = udunits2_prefix / "Library"

setup(
    include_package_data=True,
    ext_modules=[
        Extension(
            "gimli._udunits2",
            ["gimli/_udunits2.pyx"],
            libraries=["udunits2"],
            include_dirs=[str(udunits2_prefix / "include"), numpy.get_include()],
            library_dirs=[str(udunits2_prefix / "lib")],
        )
    ],
)
