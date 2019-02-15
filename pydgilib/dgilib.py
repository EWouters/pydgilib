"""This module provides Python bindings for DGILib."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: dgilib.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

GET_STRING_SIZE = 100
NUM_INTERFACES = 10
NUM_CONFIG_IDS = 255
NUM_CALIBRATION = 255
BUFFER_SIZE = 10000000
MAX_PRINT = 100

# Interface types
INTERFACE_TIMESTAMP  = 0x00 #   0 Service interface which appends timestamps to all received events on associated interfaces.
INTERFACE_SPI        = 0x20 #  32 Communicates directly over SPI in Slave mode.
INTERFACE_USART      = 0x21 #  33 Communicates directly over USART in Slave mode.
INTERFACE_I2C        = 0x22 #  34 Communicates directly over I2C in Slave mode.
INTERFACE_GPIO       = 0x30 #  48 Monitors and controls the state of GPIO pins.
INTERFACE_POWER_DATA = 0x40 #  64 Receives data from the attached power measurement co-processors.
INTERFACE_POWER_SYNC = 0x41 #  65 Receives sync events from the attached power measurement co-processors.
INTERFACE_RESERVED   = 0xFF # 255 Special identifier used to indicate no interface.

# Circuit types
OLD_XAM = 0x00 #   0
XAM     = 0x10 #  16
PAM     = 0x11 #  17
UNKNOWN = 0xFF # 255

# Return codes
IDLE               = 0x00 #   0
RUNNING            = 0x01 #   1
DONE               = 0x02 #   2
CALIBRATING        = 0x03 #   3
INIT_FAILED        = 0x10 #  16
OVERFLOWED         = 0x11 #  17
USB_DISCONNECTED   = 0x12 #  18
CALIBRATION_FAILED = 0x20 #  32

from ctypes import *
from time import sleep

from pydgilib.dgilib_exceptions import *

from pydgilib.dgilib_discovery import DGILibDiscovery
from pydgilib.dgilib_housekeeping import DGILibHousekeeping
from pydgilib.dgilib_interface_communication import DGILibInterfaceCommunication
from pydgilib.dgilib_auxiliary import DGILibAuxiliary


class DGILib(
    DGILibDiscovery, DGILibHousekeeping, DGILibInterfaceCommunication, DGILibAuxiliary
):
    """Python bindings for DGILib.
    
    DGILib is a Dynamic-Link Library (DLL) to help software applications communicate with Data Gateway
    Interface (DGI) devices. See the Data Gateway Interface user guide for further details. DGILib handles
    the low-level USB communication and adds a level of buffering for minimizing the chance of overflows.
    The library helps parse data streams of high complexity. The timestamp interface is parsed and split into
    separate buffers for each data source. The power interface is optionally parsed and calibrated using an
    auxiliary API.
    
    :Example:

    >>> with DGILib() as dgilib:
    ...     dgilib.get_major_version()
    5
    """

    def __init__(
        self,
        dgilib_path="dgilib",
        device_index=None,
        device_sn=None,
        verbose=1,
        *args,
        **kwargs,
    ):
        """
        :param dgilib_path: Path to dgilib.dll (More info at: https://www.microchip.com/developmenttools/ProductDetails/ATPOWERDEBUGGER)
        :type dgilib_path: str
        :param device_index: index of the device to use, only usefull if multiple devices are connected
            (default is None, will resolve to 0)
        :type device_index: int or None
        :param device_sn: the serial number of the device to use. Has higher priority than device_index
            (default is None, will resolve to serial number of device 0)
        :type device_sn: str or None
        :param verbose: set to a positive number to print more status messages (default is 0)
        :type verbose: int
        :raises: :exc:`DLLError`
        """

        # Load the dgilib.dll
        try:
            self.dgilib = cdll.LoadLibrary(dgilib_path)
        except OSError as e:
            raise DLLError(
                f"dgilib.dll could not be found in the specicied path: {dgilib_path}."
            )

        # DGILibDiscovery.__init__(self, *args, **kwargs)
        # DGILibHousekeeping.__init__(self, *args, **kwargs)
        # DGILibInterfaceCommunication.__init__(self, *args, **kwargs)
        # DGILibAuxiliary.__init__(self, *args, **kwargs)

        self.device_index = device_index
        self.device_sn = device_sn
        self.verbose = verbose

    def __enter__(self):
        """
        :raises: :exc:`DeviceIndexError`
        :raises: :exc:`DeviceConnectionError`
        """

        DGILibDiscovery.__enter__(self)
        DGILibHousekeeping.__enter__(self)
        # DGILibInterfaceCommunication.__enter__(self)
        DGILibAuxiliary.__enter__(self)

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        DGILibAuxiliary.__exit__(self, exc_type, exc_value, traceback)
        # DGILibInterfaceCommunication.__exit__(self, exc_type, exc_value, traceback)
        DGILibHousekeeping.__exit__(self, exc_type, exc_value, traceback)
        DGILibDiscovery.__exit__(self, exc_type, exc_value, traceback)

        if self.verbose:
            print("bye from DGILib")


#     def __contains__(self, attribute_name):
#         """Used to provide `attribute_name in object` syntax
#         """
#         return hasattr(self, attribute_name)