"""This module provides Python bindings for DGILib."""

import sys
from setuptools import setup

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner", "pytest-benchmark",
                 "pytest-cov"] if needs_pytest else []

setup(
    name="pydgilib",
    version="0.2",
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
    # tests_require=["pytest", "pytest-benchmark", "pytest-cov"],
    extras_require={
        'docs':  ["Sphinx", "sphinx_rtd_theme"],
        'test': ["pytest-runner", "pytest-benchmark", "pytest-cov"], }
)

# TODO: warn if atmel studio not installed.

# NOTE: dev install: pip install -e .[docs,test]

# Update docs:
# cd docs/_build/html
# If you have not cloned the gh-pages branch previously:
# git clone --branch gh-pages https://github.com/EWouters/pydgilib.git
# Generate the docs
# cd ../..
# make.bat html
# cd _build/html
# git add .
# $ git commit - m 'Update docs.'
# $ git push origin gh-pages
