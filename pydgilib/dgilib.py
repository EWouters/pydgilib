"""This module provides Python bindings for DGILib."""

from os import getcwd
from ctypes import cdll

from pydgilib.dgilib_exceptions import DLLError
from pydgilib.dgilib_discovery import DGILibDiscovery
from pydgilib.dgilib_housekeeping import DGILibHousekeeping
from pydgilib.dgilib_interface_communication import (
    DGILibInterfaceCommunication)
from pydgilib.dgilib_auxiliary import DGILibAuxiliary
from pydgilib.dgilib_exceptions import InstantiationError


class DGILib(object):
    """Python bindings for DGILib.

    DGILib is a Dynamic-Link Library (DLL) to help software applications
    communicate with Data Gateway Interface (DGI) devices. See the Data Gateway
    Interface user guide for further details. DGILib handles the low-level USB
    communication and adds a level of buffering for minimizing the chance of
    overflows.
    The library helps parse data streams of high complexity. The timestamp
    interface is parsed and split into separate buffers for each data source.
    The power interface is optionally parsed and calibrated using an auxiliary
    API.

    :Example:

    >>> with DGILib() as dgilib:
    ...     dgilib.get_major_version()
    5
    """

    def __init__(self, dgilib_path="dgilib.dll", *args, **kwargs):
        """Instantiate DGILib object.

        :param dgilib_path: Path to dgilib.dll (More info at:
            https://www.microchip.com/developmenttools/ProductDetailsATPOWERDEBUGGER)
        :type dgilib_path: str
        :param device_index: index of the device to use, only usefull if
            multiple devices are connected (default is None, will resolve to 0)
        :type device_index: int or None
        :param device_sn: the serial number of the device to use. Has higher
            priority than device_index (default is None, will resolve to
            serial number of device 0)
        :type device_sn: str or None
        :param verbose: set to a positive number to print more status messages
            (default is 0)
        :type verbose: int
        :raises: :exc:`DLLError`
        """
        # Load the dgilib.dll
        try:
            self.dgilib = cdll.LoadLibrary(dgilib_path)
        except OSError as e:
            raise DLLError(
                f"dgilib.dll could not be found in the specified path: "
                f"{dgilib_path}. Specify the path to the .dll or put it in "
                f"{getcwd()}. If you don't have it you can download it from "
                f"https://www.microchip.com/mplab/avr-support/data-visualizer "
                f"(download DGIlib dll, unzip the files and put the dll in "
                f"your folder.\nError:{e}")

        # Argument parsing
        self.device_index = kwargs.get("device_index", None)
        self.device_sn = kwargs.get("device_sn", None)
        self.verbose = kwargs.get("verbose", 0)

        # Instantiate modules
        self.discovery = DGILibDiscovery(self)
        self.housekeeping = DGILibHousekeeping(self)
        self.interface_communication = DGILibInterfaceCommunication(self)
        self.auxiliary = DGILibAuxiliary(self)

    def __enter__(self):
        """For usage in `with DGILib() as dgilib:` syntax."""
        DGILibDiscovery.__enter__(self)
        DGILibHousekeeping.__enter__(self)
        DGILibAuxiliary.__enter__(self)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """For usage in `with DGILib() as dgilib:` syntax."""
        DGILibAuxiliary.__exit__(self, exc_type, exc_value, traceback)
        DGILibHousekeeping.__exit__(self, exc_type, exc_value, traceback)
        DGILibDiscovery.__exit__(self, exc_type, exc_value, traceback)

        if self.verbose:
            print("bye from DGILib")

    def isDGILib(self, pydgilib):
        """Use to detect that this is a DGILib class."""
        if not isinstance(pydgilib, DGILib):
            raise InstantiationError(
                f"This class can only be instantiated with a DGILib class. Got"
                f" {pydgilib}")
