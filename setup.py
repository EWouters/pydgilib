from setuptools import setup

setup(name='pydgilib',
      version='0.1',
      description='This module provides Python bindings for DGILib',
      url='https://github.com/EWouters/Atmel-SAML11/tree/master/Python/pydgilib',
      author='Erik Wouters',
      author_email='ehwo(at)kth.se',
      license='MIT',
      packages=['pydgilib'],
      dependency_links=['https://www.microchip.com/developmenttools/ProductDetails/ATPOWERDEBUGGER'],
      zip_safe=False)