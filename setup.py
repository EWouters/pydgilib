"""This module provides Python bindings for DGILib."""

import sys
from setuptools import setup

with open("docs/README.rst", "r") as fh:
    long_description = fh.read()

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner", "pytest-benchmark",
                 "pytest-cov"] if needs_pytest else []

setup(
    name="pydgilib",
    version="0.2.3",
    description="This module provides Python bindings for DGILib.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/EWouters/pydgilib",
    author="Erik Wouters",
    author_email="ehwo@kth.se",
    license="BSD-3-Clause",
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

# Push release:
# Set version tag in setup.py and docs/conf.py
# Generate docs
# $ python setup.py sdist bdist_wheel
# $ twine upload dist/*
