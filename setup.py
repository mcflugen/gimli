import pathlib
import pkg_resources
import sys
from setuptools import setup, find_packages, Extension


def read(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read()


long_description = u'\n\n'.join(
    [
        read('README.rst'),
        read('AUTHORS.rst'),
        read('CHANGES.rst'),
    ]
)


udunits2_prefix = pathlib.Path(sys.prefix)
if sys.platform.startswith("win"):
    udunits2_prefix = udunits2_prefix / "Library"

numpy_incl = pkg_resources.resource_filename("numpy", "core/include")

setup(
    name="gimli",
    version="0.1.0",
    description="An object-oriented Python interface to udunits",
    long_description=long_description,
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="http://csdms.colorado.edu",
    python_requires=">=3.6",
    install_requires=open("requirements.txt", "r").read().splitlines(),
    include_package_data=True,
    setup_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=["units", "unit conversion", "earth science", "model coupling"],
    packages=find_packages(exclude=("tests*",)),
    entry_points={"console_scripts": ["gimli=gimli.cli:main"]},
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
