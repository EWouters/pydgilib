"""This module provides Python bindings for the Interface Communication API of DGILib."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = (
    " $Id: dgilib_interface_communication.py 1586 2019-02-13 15:56:25Z EWouters $ "
)
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

class DGILibInterfaceCommunication(object):
    """Python bindings for DGILib Interface Communication.
    
    DGILib is a Dynamic-Link Library (DLL) to help software applications communicate with Data Gateway
    Interface (DGI) devices. See the Data Gateway Interface user guide for further details. DGILib handles
    the low-level USB communication and adds a level of buffering for minimizing the chance of overflows.
    The library helps parse data streams of high complexity. The timestamp interface is parsed and split into
    separate buffers for each data source.
    """

    def interface_list(self):
        """`interface_list`
        Queries the connected DGI device for available interfaces. Refer to the DGI documentation to resolve the
        ID.
        
        `int interface_list(uint32_t dgi_hndl, unsigned char* interfaces, unsigned char* count)`
        
        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        | *interfaces* | Buffer to hold the ID of the available interfaces. Should be able to hold minimum 10 elements, but a larger count should be used to be future proof. |
        | *count* | Pointer to a variable that will be set to the number of interfaces registered in buffer. |
        +------------+------------+
        
        :return: List of available interfaces
        :rtype: list(int)
        :raises: :exc:`DeviceReturnError`
        """

        interfaces = (c_ubyte * NUM_INTERFACES)()
        interfaceCount = c_ubyte()
        res = self.dgilib.interface_list(
            self.dgi_hndl, byref(interfaces), byref(interfaceCount)
        )
        if self.verbose:
            print(
                f"\t{res} interface_list: {interfaces[:interfaceCount.value]}, interfaceCount: {interfaceCount.value}"
            )
        if res:
            raise DeviceReturnError(f"interface_list returned: {res}")

        return interfaces[: interfaceCount.value]

    def interface_enable(self, interface_id, timestamp=True):
        """`interface_enable`
        Enables the specified interface. Note that no data acquisition will begin until a session has been started.

        `int interface_enable(uint32_t dgi_hndl, int interface_id, bool timestamp)`
     
        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        | *interface_id* | The ID of the interface to enable. |
        | *timestamp* | Setting this to true will make the interface use timestamping. Consult the DGI documentation for details on the timestamping option. |
        +------------+------------+
        
        :param interface_id: The ID of the interface to enable
        :type interface_id: int
        :param timestamp: Setting this to true will make the interface use timestamping (defaults to True)
        :type timestamp: bool
        :raises: :exc:`DeviceReturnError`
        """

        res = self.dgilib.interface_enable(self.dgi_hndl, interface_id, timestamp)
        if self.verbose:
            print(f"\t{res} interface_enable: {interface_id}, timestamp: {timestamp}")
        if res:
            raise DeviceReturnError(
                f"interface_enable: {interface_id}, timestamp: {timestamp} returned: {res}"
            )

    def interface_disable(self, interface_id):
        """`interface_disable`
        Disables the specified interface.

        `int interface_disable(uint32_t dgi_hndl, int interface_id)`
     
        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        | *interface_id* | The ID of the interface to disable. |
        +------------+------------+
        
        :param interface_id: The ID of the interface to disable
        :type interface_id: int
        :raises: :exc:`DeviceReturnError`
        """

        res = self.dgilib.interface_disable(self.dgi_hndl, interface_id)
        if self.verbose:
            print(f"\t{res} interface_disable: {interface_id}")
        if res:
            raise DeviceReturnError(f"interface_disable returned: {res}")

    def interface_get_configuration(self, interface_id):
        """`interface_get_configuration`
        Gets the configuration associated with the specified interface. Consult the DGI documentation for details.

        `int interface_get_configuration(uint32_t dgi_hndl, int interface_id, unsigned int* config_id, unsigned int*
        config_value, unsigned int* config_cnt)`
     
        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle to connection |
        | *interface_id* | The ID of the interface |
        | *config_id* | Buffer that will hold the ID field for the configuration item |
        | *config_value* | Buffer that will hold the value field for the configuration item |
        | *config_cnt* | Pointer to variable that will hold the count of stored configuration items |
        +------------+------------+
        
        :param interface_id: The ID of the interface
        :type interface_id: int
        :return: Tuple of a list of configuration IDs and a list of configuration values
        :rtype: tuple(list(int), list(int))
        :raises: :exc:`DeviceReturnError`
        """

        config_id = (c_uint * NUM_CONFIG_IDS)()
        config_value = (c_uint * NUM_CONFIG_IDS)()
        config_cnt = c_uint()
        res = self.dgilib.interface_get_configuration(
            self.dgi_hndl,
            interface_id,
            byref(config_id),
            byref(config_value),
            byref(config_cnt),
        )
        if self.verbose:
            print(
                f"\t{res} interface_get_configuration: {interface_id}, config_cnt: {config_cnt.value}"
            )
        if self.verbose >= 2:
            for i in range(config_cnt.value):
                print(f"\t\tconfig_id: {config_id[i]},\tvalue: {config_value[i]}")
        if res:
            raise DeviceReturnError(
                f"interface_get_configuration: {interface_id}, timestamp: {timestamp} returned: {res}"
            )

        return config_id[: config_cnt.value], config_value[: config_cnt.value]

    def interface_set_configuration(self, interface_id, config_id, config_value):
        """`interface_set_configuration`
        Sets the given configuration fields for the specified interface. Consult the DGI documentation for details.

        `int interface_set_configuration(uint32_t dgi_hndl, int interface_id, unsigned int* config_id, unsigned int*
        config_value, unsigned int config_cnt)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle to connection |
        | *interface_id* | The ID of the interface |
        | *config_id* | Buffer that holds the ID field for the configuration items to set |
        | *config_value* | Buffer that holds the value field for the configuration items to set |
        | *config_cnt* | Number of items to set |
        +------------+------------+
        
        :param interface_id: The ID of the interface
        :type interface_id: int
        :param config_id: List that holds the ID field for the configuration items to set
        :type config_id: list(int)
        :param config_value: List that holds the value field for the configuration items to set (must have the same
            number of elements as config_id)
        :type config_value: list(int)
        :raises: :exc:`DeviceArgumentError`
        :raises: :exc:`DeviceReturnError`
        """

        if len(config_id) == len(config_value):
            config_cnt = c_uint(len(config_id))
        else:
            raise DeviceArgumentError(
                f"interface_set_configuration: the lenght of config_id list ({len(config_id)}) is not equal to the lenght of config_value list ({len(config_value)})"
            )

        config_id = (c_uint * NUM_CONFIG_IDS)(*config_id)
        config_value = (c_uint * NUM_CONFIG_IDS)(*config_value)
        res = self.dgilib.interface_set_configuration(
            self.dgi_hndl,
            interface_id,
            byref(config_id),
            byref(config_value),
            config_cnt,
        )
        if self.verbose:
            print(
                f"\t{res} interface_set_configuration: {interface_id}, config_cnt: {config_cnt.value}"
            )
        if self.verbose >= 2:
            for i in range(config_cnt.value):
                print(f"\t\tconfig_id: {config_id[i]},\tvalue: {config_value[i]}")
        if res:
            raise DeviceReturnError(
                f"interface_set_configuration: {interface_id} returned: {res}"
            )

    def interface_clear_buffer(self, interface_id):
        """`interface_clear_buffer`
        Clears the data in the buffers for the specified interface.

        `int interface_clear_buffer(uint32_t dgi_hndl, int interface_id)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        | *interface_id* | The ID of the interface |
        +------------+------------+
        
        :param interface_id: The ID of the interface
        :type interface_id: int
        :raises: :exc:`DeviceReturnError`
        """

        res = self.dgilib.interface_clear_buffer(self.dgi_hndl, interface_id)
        if self.verbose:
            print(f"\t{res} interface_clear_buffer: {interface_id}")
        if res:
            raise DeviceReturnError(f"interface_clear_buffer returned: {res}")

    def interface_read_data(self, interface_id):
        """`interface_read_data`
        Reads the data received on the specified interface. This should be called regularly to avoid overflows in
        the system. DGILib can buffer 10M samples.

        `int interface_read_data(uint32_t dgi_hndl, int interface_id, unsigned char* buffer, unsigned long long*
        timestamp, int* length, unsigned int* ovf_index, unsigned int* ovf_length, unsigned int* ovf_entry_count)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        | *interface_id* | The ID of the interface |
        | *buffer* | Buffer that will hold the received data. The buffer must have allocated 10M elements. |
        | *timestamp* | If timestamp is enabled for the interface, the buffer that will hold the received data. The buffer must have allocated 10M elements. Otherwise send 0. |
        | *length* | Pointer to a variable that will hold the count of elements received |
        | *ovf_index* | Reserved. Set to 0. |
        | *ovf_length* | Reserved. Set to 0. |
        | *ovf_entry_count* | Reserved. Set to 0. Could be set to a pointer to a variable that can be used as an indicator of overflows. Overflow would be indicated by non-zero value. |
        +------------+------------+
        
        :param interface_id: The ID of the interface
        :type interface_id: int
        :return: Tuple of a list of received values and a list of ticks
        :rtype: tuple(list(int), list(int))
        :raises: :exc:`DeviceReturnError`
        """

        buffer = (c_ubyte * BUFFER_SIZE)()
        ticks = (c_ulonglong * BUFFER_SIZE)()
        length = c_uint(0)
        ovf_index = c_uint(0)
        ovf_length = c_uint(0)
        ovf_entry_count = c_uint(0)
        res = self.dgilib.interface_read_data(
            self.dgi_hndl,
            interface_id,
            buffer,
            ticks,
            byref(length),
            byref(ovf_index),
            byref(ovf_length),
            byref(ovf_entry_count),
        )
        if self.verbose:
            print(
                f"\t{res} interface_read_data: {interface_id}, length: {length.value}"
            )
        if self.verbose >= 2:
            for i in range(length.value):
                print(f"\t{i}:\tbuffer: {buffer[i]},\ttick: {ticks[i]}")
        if res:
            raise DeviceReturnError(
                f"interface_read_data: {interface_id} returned: {res}"
            )

        return buffer[: length.value], ticks[: length.value]

    def interface_write_data(self, interface_id, buffer):
        """`interface_write_data`
        Writes data to the specified interface. A maximum of 255 elements can be written each time. An error
        return code will be given if data hasn't been written yet.

        TODO: A non-zero return value indicates an error. An error will be returned if the interface is still in the process of
        writing data. Wait a while and try again. The function get_connection_status can be used to verify if there
        is an error condition.

        `int interface_write_data(uint32_t dgi_hndl, int interface_id, unsigned char* buffer, int* length)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *dgi_hndl* | Handle of the connection |
        | *interface_id* | The ID of the interface |
        | *buffer* | Buffer that holds the data to write. The buffer must have allocated 10M elements |
        | *length* | Pointer to a variable that will hold the count of elements received |
        +------------+------------+
        
        :param interface_id: The ID of the interface
        :type interface_id: int
        :param buffer: Buffer that holds the data to write (defaults to None)
        :type buffer: int
        :raises: :exc:`DeviceReturnError`
        """

        length = c_uint(len(buffer))
        buffer = (c_ubyte * BUFFER_SIZE)(*buffer)
        res = self.dgilib.interface_write_data(
            self.dgi_hndl, interface_id, byref(buffer), byref(length)
        )
        if self.verbose:
            print(
                f"\t{res} interface_write_data: {interface_id}, length: {length.value}"
            )
        if self.verbose >= 2:
            for i in range(length.value):
                print(f"\t{i}:\tbuffer: {buffer[i]}")
        if res:
            raise DeviceReturnError(
                f"TODOTODOTODO: interface_write_data: {interface_id} returned: {res}"
            )