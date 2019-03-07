"""This module provides Python bindings for the Discovery API of DGILib."""

from ctypes import byref, create_string_buffer

from pydgilib.dgilib_config import GET_STRING_SIZE
from pydgilib.dgilib_exceptions import DeviceReturnError


class DGILibDiscovery(object):
    """Python bindings for DGILib Discovery.

    DGILib is a Dynamic-Link Library (DLL) to help software applications
    communicate with Data Gateway Interface (DGI) devices. See the Data
    Gateway Interface user guide for further details. DGILib handles
    the low-level USB communication and adds a level of buffering for
    minimizing the chance of overflows.

    TODO?
    2.1.1. initialize_status_change_notification
    Initializes the system necessary for using the status change notification
    callback mechanisms. A handle will be created to keep track of the
    registered callbacks. This function must always be called before
    registering and unregistering notification callbacks.
    Function definition
    void initialize_status_change_notification(uint32_t* handlep)
    Parameters
    handlep Pointer to a variable that will hold the handle
    2.1.2. uninitialize_status_change_notification
    Uninitializes the status change notification callback mechanisms. This
    function must be called when shutting down to clean up memory allocations.
    Function definition
    void uninitialize_status_change_notification(uint32_t handle)
    Parameters
    handle Handle to uninitialize
    2.1.3. register_for_device_status_change_notifications
    Registers provided function pointer with the device status change
    mechanism. Whenever there is a change (device connected or disconnected)
    the callback will be executed. Note that it is not allowed to connect to a
    device in the context of the callback function. The callback function has
    the following definition: typedef void (*DeviceStatusChangedCallBack)(char*
    device_name, char* device_serial, BOOL connected)
    Function definition
    void register_for_device_status_change_notifications(uint32_t handle,
    DeviceStatusChangedCallBack deviceStatusChangedCallBack)
    Parameters
    handle Handle to change notification mechanisms
    deviceStatusChangedCallBack Function pointer that will be called when the
    devices change
    2.1.4. unregister_for_device_status_change_notifications
    Unregisters previously registered function pointer from the device status
    change mechanism.
    Function definition
    void unregister_for_device_status_change_notifications(uint32_t handle,
    DeviceStatusChangedCallBack deviceStatusChangedCallBack)
    Parameters
    handle Handle to change notification mechanisms
    deviceStatusChangedCallBack Function pointer that will be removed

    """

    dgilib = None
    verbose = None

    def discover(self):
        """`discover`.

        Triggers a scan to find available devices in the system. The result
        will be immediately available through the `get_device_count`,
        `get_device_name` and `get_device_serial` functions.

        `void discover(void)`
        """
        self.dgilib.discover()

    def get_device_count(self):
        """`get_device_count`.

        Returns the number of devices detected.

        `int get_device_count(void)`

        :return: The number of devices detected
        :rtype: int
        """
        device_count = self.dgilib.get_device_count()
        if self.verbose:
            print(f"device_count: {device_count}")
        return device_count

    def get_device_name(self, index=0):
        """`get_device_name`.

        Gets the name of a detected device.

        `int get_device_name(int index, char* name)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *index* | Index of device ranges from 0 to `get_device_count` - 1 |
        | *name* | Pointer to buffer where name of device can be stored. 100
        or more bytes must be allocated |
        +------------+------------+

        :param index: Index of device ranges from 0 to `get_device_count` - 1
        :type index: int
        :return: The name of a detected device
        :rtype: str
        :raises: :exc:`DeviceReturnError`
        """
        name = create_string_buffer(GET_STRING_SIZE)
        res = self.dgilib.get_device_name(index, byref(name))
        if self.verbose:
            print(f"\t{res} get_device_name: {name.value}")
        if res:
            raise DeviceReturnError(f"get_device_name returned: {res}")
        return name.value

    def get_device_serial(self, index=0):
        """`get_device_serial`.

        Gets the serial number of a detected device.

        `int get_device_serial(int index, char* sn)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *index* | Index of device ranges from 0 to `get_device_count` - 1 |
        | *sn* | Pointer to buffer where the serial number of the device can
        be stored. 100 or more bytes must be allocated. This is used when
        connecting to a device |
        +------------+------------+

        :param index: Index of device ranges from 0 to `get_device_count` - 1
        :type index: int
        :return: The serial number of a detected device
        :rtype: str
        :raises: :exc:`DeviceReturnError`
        """
        device_sn = create_string_buffer(GET_STRING_SIZE)
        res = self.dgilib.get_device_serial(index, byref(device_sn))
        if self.verbose:
            print(f"\t{res} get_device_serial: {device_sn.value}")
        if res:
            raise DeviceReturnError(f"get_device_serial returned: {res}")
        return device_sn.value

    def is_msd_mode(self, device_sn):
        """`is_msd_mode`.

        EDBG devices can be set to a mass storage mode where the DGI is
        unavailable. In such cases the device is still detected by DGILib, but
        it won't be possible to directly connect to it. This command is used
        to check if the device is in such a mode.

        A non-zero return value indicates that the mode must be changed by
        `set_mode` before proceeding.

        `int is_msd_mode(char* sn)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *sn* | Serial number of the device to check |
        +------------+------------+

        :param device_sn: Serial number of the device to check (defaults to
            self.device_sn)
        :type device_sn: str or None
        :return: A non-zero return value indicates that the mode must be
            changed by `set_mode` before proceeding.
        :rtype: int
        """
        msd_mode = self.dgilib.is_msd_mode(device_sn)
        if self.verbose:
            print(f"msd_mode: {msd_mode}")
        return msd_mode

    def set_mode(self, device_sn, nmbed=1):
        """`set_mode`.

        This function is used to temporarily set the EDBG to a specified mode.

        `int set_mode(char* sn, int nmbed)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *sn* | Serial number of the device to set |
        | *nmbed* | 0 - Set to mbed mode. 1 - Set to DGI mode |
        +------------+------------+

        :param device_sn: Serial number of the device to set
        :type device_sn: str
        :param nmbed: 0 - Set to mbed mode. 1 - Set to DGI mode (defaults to
            DGI mode)
        :type nmbed: int
        :raises: :exc:`DeviceReturnError`
        """
        res = self.dgilib.set_mode(device_sn, nmbed)
        if self.verbose:
            print(f"\t{res} set_mode {nmbed}")
        if res:
            raise DeviceReturnError(f"set_mode returned: {res}")
