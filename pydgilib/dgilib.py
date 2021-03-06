"""This module provides Python bindings for DGILib."""

from os import (path, getcwd, getenv)
from ctypes import cdll

from pydgilib.dgilib_exceptions import (
    DLLError, DeviceIndexError, DeviceConnectionError)
from pydgilib.dgilib_discovery import DGILibDiscovery
from pydgilib.dgilib_housekeeping import DGILibHousekeeping
from pydgilib.dgilib_interface_communication import (
    DGILibInterfaceCommunication)
from pydgilib.dgilib_auxiliary import DGILibAuxiliary


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

    # Add modules
    # Discovery
    # discovery = DGILibDiscovery
    discover = DGILibDiscovery.discover
    get_device_count = DGILibDiscovery.get_device_count
    get_device_name = DGILibDiscovery.get_device_name
    get_device_serial = DGILibDiscovery.get_device_serial
    is_msd_mode = DGILibDiscovery.is_msd_mode
    set_mode = DGILibDiscovery.set_mode

    # Housekeeping
    # housekeeping = DGILibHousekeeping
    connect = DGILibHousekeeping.connect
    disconnect = DGILibHousekeeping.disconnect
    connection_status = DGILibHousekeeping.connection_status
    get_major_version = DGILibHousekeeping.get_major_version
    get_minor_version = DGILibHousekeeping.get_minor_version
    get_build_number = DGILibHousekeeping.get_build_number
    get_fw_version = DGILibHousekeeping.get_fw_version
    start_polling = DGILibHousekeeping.start_polling
    stop_polling = DGILibHousekeeping.stop_polling
    target_reset = DGILibHousekeeping.target_reset

    # Interface Communication
    # interface_communication = DGILibInterfaceCommunication
    interface_list = DGILibInterfaceCommunication.interface_list
    interface_enable = DGILibInterfaceCommunication.interface_enable
    interface_disable = DGILibInterfaceCommunication.interface_disable
    interface_get_configuration = DGILibInterfaceCommunication.interface_get_configuration
    interface_set_configuration = DGILibInterfaceCommunication.interface_set_configuration
    interface_clear_buffer = DGILibInterfaceCommunication.interface_clear_buffer
    interface_read_data = DGILibInterfaceCommunication.interface_read_data
    interface_write_data = DGILibInterfaceCommunication.interface_write_data

    # Auxiliary
    # auxiliary = DGILibAuxiliary
    auxiliary_power_initialize = DGILibAuxiliary.auxiliary_power_initialize
    auxiliary_power_uninitialize = DGILibAuxiliary.auxiliary_power_uninitialize
    auxiliary_power_register_buffer_pointers = DGILibAuxiliary.auxiliary_power_register_buffer_pointers
    auxiliary_power_unregister_buffer_pointers = DGILibAuxiliary.auxiliary_power_unregister_buffer_pointers
    auxiliary_power_calibration_is_valid = DGILibAuxiliary.auxiliary_power_calibration_is_valid
    auxiliary_power_trigger_calibration = DGILibAuxiliary.auxiliary_power_trigger_calibration
    auxiliary_power_get_calibration = DGILibAuxiliary.auxiliary_power_get_calibration
    auxiliary_power_get_circuit_type = DGILibAuxiliary.auxiliary_power_get_circuit_type
    auxiliary_power_get_status = DGILibAuxiliary.auxiliary_power_get_status
    auxiliary_power_start = DGILibAuxiliary.auxiliary_power_start
    auxiliary_power_stop = DGILibAuxiliary.auxiliary_power_stop
    auxiliary_power_lock_data_for_reading = DGILibAuxiliary.auxiliary_power_lock_data_for_reading
    auxiliary_power_copy_data = DGILibAuxiliary.auxiliary_power_copy_data
    auxiliary_power_free_data = DGILibAuxiliary.auxiliary_power_free_data

    def __init__(self, *args, **kwargs):
        """__init__.

        Parameters
        ----------
        dgilib_path : str
            Path to dgilib.dll (More info at:
            https://www.microchip.com/developmenttools/ProductDetailsATPOWERDEBUGGER)

        device_index : int or None
            Index of the device to use, only useful if multiple devices are
            connected (default is `None`, will resolve to `0`)

        device_sn : str or None
            The serial number of the device to use. Has higher
            priority than device_index (default is `None`, will resolve to
            serial number of device `0`)

        verbose : int
            Set to a positive number to print more status messages
            (default is `0`)

        Raises
        -------
            DLLError
                TODO: `Not documented yet.`

        """
        # Load the dgilib.dll
        dgilib_path = kwargs.get(
            "dgilib_path", args[0] if args else "dgilib.dll")
        for location in (dgilib_path, [dgilib_path], [getcwd(), "dgilib.dll"],
                         [getcwd(), dgilib_path], [getenv(
                             "programfiles(x86)"), "Atmel", "Studio", "7.0",
                             "Extensions", "Application", "dgilib.dll"]):
            try:
                self.dgilib = cdll.LoadLibrary(path.join(*location))
            except OSError:
                continue
            break
        else:
            raise DLLError(
                f"Could not find dgilib.dll. If you install Atmel Studio in " +
                f"the default location (" + path.join(
                    getenv("programfiles(x86)"), "Atmel", "Studio", "7.0") +
                f") it should get loaded automatically. Alternatively you " +
                f"can download it from https://www.microchip.com/mplab/avr-" +
                f"support/data-visualizer (download DGIlib dll, unzip the " +
                f"files and put the dll in {getcwd()}) or specify the path " +
                f"as the first argument or as a keyword argument " +
                f"(dgilib_path). Got dgilib_path={dgilib_path}.")

        # Argument parsing
        self.device_index = kwargs.get("device_index", None)
        self.device_sn = kwargs.get("device_sn", None)
        self.verbose = kwargs.get("verbose", 0)

        self.dgi_hndl = None
        self.power_hndl = None

        # Instantiate modules
        # self.discovery(self)
        # self.housekeeping(self)
        # self.interface_communication(self)
        # self.auxiliary(self)

    def __enter__(self):
        """__enter__

        For usage in ``with DGILib() as dgilib:`` syntax.

        """
        # Discovery
        self.discover()
        device_count = self.get_device_count()

        if self.device_sn is None:
            if self.device_index is None:
                self.device_index = 0
            elif self.device_index > device_count - 1:
                raise DeviceIndexError(
                    f"Discovered {device_count} devices so could not select "
                    f"device with index {self.device_index}."
                )
            self.device_sn = self.get_device_serial(self.device_index)

        # UNTESTED:
        # if self.is_msd_mode(self.device_sn):
        #     res = self.set_mode(self.device_sn, 1)
        #     print(f"\t{res} set_mode 1")

        # Housekeeping
        self.dgi_hndl = self.connect(self.device_sn)
        c_status = self.connection_status()
        if c_status:
            raise DeviceConnectionError(
                f"Could not connect to device. Connection status: {c_status}.")

        # Interface communication

        # Auxiliary

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """__exit__

        For usage in ``with DGILib() as dgilib:`` syntax.

        """
        # Discovery

        # Housekeeping
        self.disconnect()

        # Interface communication

        # Auxiliary
