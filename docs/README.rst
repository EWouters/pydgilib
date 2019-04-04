Pydgilib provides python bindings for Atmel® Data Gateway Interface (DGI) devices.
See the `Data Gateway Interface user guide <http://ww1.microchip.com/downloads/en/DeviceDoc/40001905B.pdf>`_
for further details. This package works best if you have `Atmel Studio 7.0 <https://www.microchip.com/mplab/avr-support/atmel-studio-7>`_
installed. If you do it will automatically make use of the installed files it requires. Otherwise you can
download the required DLL from Atmel `here <https://www.microchip.com/developmenttools/ProductDetails/ATPOWERDEBUGGER>`_
and point pydgilib to the location where you downloaded the file.

Features
========

The main features of this library are:

* It wraps the C functions of DGILib in python `functions <source/pydgilib.html#pydgilib.dgilib.DGILib>`_

* It provides a `class <source/pydgilib_extra.html#module-pydgilib_extra.dgilib_extra>`_ to easily log data from the power and gpio interfaces to a `.csv` file or a plot (using `matplotlib <https://matplotlib.org/>`_)

* It provides a `function <source/atprogram.html#atprogram-package>`_ that wraps `atprogram.exe` and `make.exe` so it can compile projects and flash them to a board

The documentation of all the functions can be found in this `overview <py-modindex.html>`_ or this `list <genindex.html>`_.

Installation
============

You will need to install pydgilib in a **32-bit Python** environment on Windows because `DGILib.dll` is compiled for 32-bit. Other operating systems are not supported.

Static Installation
-------------------

If you want to install a static copy you can run::

    $ pip install git+https://github.com/EWouters/pydgilib

Development Installation
------------------------

1. Clone the repo::

    $ git clone https://github.com/EWouters/pydgilib.git

2. Install symlinked to repo::

    $ pip install -e .

 If you want to be able to run the tests or compile the docs run instead::

    $ pip install -e .[test,docs]

Getting Started
===============

1. Connect your device that supports DGI

2. Print the serial number of your device::

    >>> from pydgilib import DGILib
    >>> with DGILib() as dgilib:
    ...     print(dgilib.device_sn)
    ...
    b'ATML3138061800001604'

3. Log the current of the board and the states of the gpio pins for one second and write the results to `.csv` files::

    >>> from pydgilib_extra import DGILibExtra
    >>> with DGILibExtra() as dgilib:
    ...     dgilib.logger.log(1)
    ...

4. Log the current of the board and the states of the gpio pins for one second and show a plot of the results::

    >>> from pydgilib_extra import DGILibExtra, LOGGER_PLOT
    >>> with DGILibExtra(loggers=[LOGGER_PLOT]) as dgilib:
    ...     dgilib.logger.log(1)
    ...
    {48: <pydgilib_extra.dgilib_data.InterfaceData object at 0x00F22A90>, 256: <pydgilib_extra.dgilib_data.InterfaceData object at 0x00F229F0>}

 .. figure:: source/images/plot_example.png
    :alt: plot example

    Plot of a SAML11 board running the unit test project.