"""This module provides Python bindings for the Housekeeping API of DGILib."""

from ctypes import (byref, c_uint, c_ubyte)

from pydgilib.dgilib_exceptions import (
    DeviceConnectionError, DeviceReturnError)


class DGILibHousekeeping(object):
    """Python bindings for DGILib Housekeeping.

    DGILib is a Dynamic-Link Library (DLL) to help software applications
    communicate with Data Gateway Interface (DGI) devices. See the Data
    Gateway Interface user guide for further details. DGILib handles the
    low-level USB communication and adds a level of buffering for minimizing
    the chance of overflows.
    The library helps parse data streams of high complexity.
    """

    def __init__(self, pydgilib):
        """Populate pydgilib attribute."""
        pydgilib.isDGILib()
        self.pydgilib = pydgilib
        # Make methods available in pydgilib.
        self.pydgilib.connect = self.connect
        self.pydgilib.disconnect = self.disconnect
        self.pydgilib.connection_status = self.connection_status
        self.pydgilib.get_major_version = self.get_major_version
        self.pydgilib.get_minor_version = self.get_minor_version
        self.pydgilib.get_build_number = self.get_build_number
        self.pydgilib.get_fw_version = self.get_fw_version
        self.pydgilib.start_polling = self.start_polling
        self.pydgilib.stop_polling = self.stop_polling
        self.pydgilib.target_reset = self.target_reset

    def __enter__(self):
        """For usage in `with DGILib() as dgilib:` syntax.

        :raises: :exc:`DeviceConnectionError`
        """
        self.pydgilib.dgi_hndl = self.connect(self.pydgilib.device_sn)
        c_status = self.connection_status()
        if c_status:
            raise DeviceConnectionError(
                f"Could not connect to device. Connection status: {c_status}."
            )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """For usage in `with DGILib() as dgilib:` syntax."""
        self.disconnect()
        if self.pydgilib.verbose:
            print("bye from Housekeeping")

    def connect(self, device_sn):
        """`connect`.

        Opens a connection to the specified device. This function must be
        called prior to any function requiring the connection handle.

        `int connect(char* sn, uint32_t* dgi_hndl_p)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *sn* | Buffer holding the serial number of the device to open a
        connection to |
        | *dgi_hndl_p* | Pointer to a variable that will hold the handle of the
        connection |
        +------------+------------+

        :param device_sn: Serial number of the device
        :type device_sn: str
        :return: Variable that holds the handle of the connection
        :rtype: c_uint()
        :raises: :exc:`DeviceReturnError`
        """
        dgi_hndl = c_uint()  # Create the dgi_hndl

        # Initialize (not in manual, exists in dgilib.h)
        # self.pydgilib.dgilib.Initialize(byref(dgi_hndl))

        res = self.pydgilib.dgilib.connect(device_sn, byref(dgi_hndl))
        if self.pydgilib.verbose:
            print(f"\t{res} connect")
        if res:
            raise DeviceReturnError(f"connect returned: {res}")

        return dgi_hndl

    def disconnect(self):
        """`disconnect`.

        Closes the specified connection.

        `int disconnect(uint32_t dgi_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        +------------+------------+

        :raises: :exc:`DeviceReturnError`
        """
        res = self.pydgilib.dgilib.disconnect(self.pydgilib.dgi_hndl)
        if self.pydgilib.verbose:
            print(f"\t{res} disconnect")
        if res:
            raise DeviceReturnError(f"disconnect returned: {res}")

        # UnInitialize (not in manual, exists in dgilib.h)
        # self.pydgilib.dgilib.UnInitialize(dgi_hndl)

    def connection_status(self):
        """`connection_status`.

        Verifies that the specified connection is still open.

        `int connection_status(uint32_t* dgi_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        +------------+------------+

        :return: A non-zero return value indicates a connection error.
        :rtype: int
        """
        c_status = self.pydgilib.dgilib.connection_status(
            self.pydgilib.dgi_hndl)
        if self.pydgilib.verbose:
            print(f"connection_status: {c_status}")

        return c_status

    def get_major_version(self):
        """`get_major_version`.

        Get the major version of the DGI library.

        `int get_major_version(void)`

        :return: The major version of the DGI library
        :rtype: int
        """
        major_version = self.pydgilib.dgilib.get_major_version()

        if self.pydgilib.verbose:
            print(f"major_version: {major_version}")

        return major_version

    def get_minor_version(self):
        """`get_minor_version`.

        Get the minor version of the DGI library.

        `int get_minor_version(void)`

        :return: The minor version of the DGI library
        :rtype: int
        """
        minor_version = self.pydgilib.dgilib.get_minor_version()

        if self.pydgilib.verbose:
            print(f"minor_version: {minor_version}")

        return minor_version

    def get_build_number(self):
        """`get_build_number`.

        Get the major version of the DGI library.

        Returns the build number of DGILib. If not supported, returns 0.

        `int get_build_number(void)`

        :return: The build number of DGILib. If not supported, returns 0.
        :rtype: int
        """
        build_number = self.pydgilib.dgilib.get_build_number()

        if self.pydgilib.verbose:
            print(f"build_number: {build_number}")

        return build_number

    def get_fw_version(self):
        """`get_fw_version`.

        Gets the firmware version of the DGI device connected. Note that this
        is the version of the DGI device, and not the tool.

        `int get_fw_version(uint32_t dgi_hndl, unsigned char* major, unsigned
        char* minor)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        | *major* | Pointer to a variable where the major version will be
        stored |
        | *minor* | Pointer to a variable where the minor version will be
        stored |
        +------------+------------+

        :return: Version information of the DGI device:
            - major_fw: the major firmware version of the DGI device connected
            - minor_fw: the minor firmware version of the DGI device connected
        :rtype: tuple(int, int)
        """
        major_fw = c_ubyte()
        minor_fw = c_ubyte()
        res = self.pydgilib.dgilib.get_fw_version(
            self.pydgilib.dgi_hndl, byref(major_fw), byref(minor_fw))
        if self.pydgilib.verbose:
            print(f"\t{res} get_fw_version")
        if res:
            raise DeviceReturnError(f"get_fw_version returned: {res}")
        if self.pydgilib.verbose:
            print(f"major_fw: {major_fw.value}\nminor_fw: {minor_fw.value}")

        return major_fw.value, minor_fw.value

    def start_polling(self):
        """`start_polling`.

        This function will start the polling system and start acquisition on
        enabled interfaces. It is possible to enable/disable interfaces both
        before and after the polling has been started. However, no data will be
        transferred until the polling is started.

        `int start_polling(uint32_t dgi_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        +------------+------------+

        :param dgi_hndl: Handle of the connection
        :type dgi_hndl: c_uint()
        :raises: :exc:`DeviceReturnError`
        """
        res = self.pydgilib.dgilib.start_polling(self.pydgilib.dgi_hndl)
        if self.pydgilib.verbose:
            print(f"\t{res} start_polling")
        if res:
            raise DeviceReturnError(f"start_polling returned: {res}")

    def stop_polling(self):
        """`stop_polling`.

        This function will stop the polling system and stop acquisition on all
        interfaces.

        `int stop_polling(uint32_t dgi_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        +------------+------------+

        :param dgi_hndl: Handle of the connection
        :type dgi_hndl: c_uint()
        :raises: :exc:`DeviceReturnError`
        """
        res = self.pydgilib.dgilib.stop_polling(self.pydgilib.dgi_hndl)
        if self.pydgilib.verbose:
            print(f"\t{res} stop_polling")
        if res:
            raise DeviceReturnError(f"stop_polling returned: {res}")

    def target_reset(self, hold_reset):
        """`target_reset`.

        This function is used to control the state of the reset line connected
        to the target, if available.

        `int target_reset(uint32_t dgi_hndl, bool hold_reset)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        | *hold_reset* | True will assert reset, false will release it |
        +------------+------------+

        :param hold_reset: True will assert reset, False will release it
        :type hold_reset: bool
        :raises: :exc:`DeviceReturnError`
        """
        res = self.pydgilib.dgilib.target_reset(
            self.pydgilib.dgi_hndl, hold_reset)
        if self.pydgilib.verbose:
            print(f"\t{res} target_reset")
        if res:
            raise DeviceReturnError(f"target_reset returned: {res}")
