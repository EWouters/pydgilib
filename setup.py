"""This module provides Python bindings for DGILib."""

import sys
from setuptools import setup

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setup(
    name="pydgilib",
    version="0.1",
    description="This module provides Python bindings for DGILib.",
    url="https://github.com/EWouters/pydgilib",
    author="Erik Wouters",
    author_email="ehwo(at)kth.se",
    license="MIT",
    packages=["pydgilib", "pydgilib_extra", "atprogram"],
    dependency_links=[
        "https://www.microchip.com/developmenttools/ProductDetails/" +
            "ATPOWERDEBUGGER"
    ],
    zip_safe=False,
    setup_requires=[
        # ... (other setup requirements)
    ] + pytest_runner,
    tests_require=["pytest", "pytest-benchmark", "pytest-cov"],
)

# TODO: warn if atmel studio not installed.
