"""This module provides Python bindings for the Auxiliary API of DGILib."""

# from ctypes import *
from ctypes import (byref, c_uint, c_float, c_double, c_int, c_size_t, c_ubyte)

from pydgilib.dgilib_config import (
    BUFFER_SIZE, XAM, NUM_CALIBRATION, MAX_PRINT)
from pydgilib.dgilib_exceptions import DeviceReturnError


class DGILibAuxiliary(object):
    """Python bindings for DGILib Auxiliary.

    DGILib is a Dynamic-Link Library (DLL) to help software applications
    communicate with Data Gateway Interface (DGI) devices. See the Data Gateway
    Interface user guide for further details. DGILib handles the low-level USB
    communication and adds a level of buffering for minimizing the chance of
    overflows. The library helps parse data streams of high complexity. The
    timestamp interface is parsed and split into separate buffers for each
    data source. The power interface is optionally parsed and calibrated using
    an auxiliary API.

    Power
    The power interface (as found on some EDBG kits and Power Debugger) uses a
    protocol stream and calibration scheme that can be tricky to get right. The
    data rates are also relatively high and the calibration procedure could
    cause issues if not handled efficiently. Therefore some auxiliary
    functions to help with this have been made to perform parsing and
    calibration.
    """

    dgilib = None
    verbose = None
    dgi_hndl = None
    power_hndl = None

    def auxiliary_power_initialize(self):
        """`auxiliary_power_initialize`.

        Initializes the power parser.

        `int auxiliary_power_initialize(uint32_t* power_hndl_p, uint32_t
        dgi_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl_p* | Pointer to variable that will hold the handle to
        the power parser |
        | *dgi_hndl* | Handle of the connection |
        +------------+------------+

        :return: Handle of the power parser
        :rtype: c_uint()
        :raises: :exc:`DeviceReturnError`
        """
        power_hndl = c_uint()

        res = self.dgilib.auxiliary_power_initialize(
            byref(power_hndl), self.dgi_hndl)
        if self.verbose:
            print(f"\t{res} auxiliary_power_initialize")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_initialize returned: {res}")

        return power_hndl

    def auxiliary_power_uninitialize(self):
        """`auxiliary_power_uninitialize`.

        Uninitializes the power parser.

        `int auxiliary_power_uninitialize(uint32_t power_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        +------------+------------+

        :raises: :exc:`DeviceReturnError`
        """
        res = self.dgilib.auxiliary_power_uninitialize(
            self.power_hndl)
        if self.verbose:
            print(f"\t{res} auxiliary_power_uninitialize")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_uninitialize returned: {res}")

    def auxiliary_power_register_buffer_pointers(
            self, channel=0, power_type=0, max_count=BUFFER_SIZE):
        """`auxiliary_power_register_buffer_pointers`.

        Registers a set of pointers to be used for storing the
        calibrated power data. The buffers can then be locked by
        auxiliary_power_lock_data_for_reading, and the data directly read from
        the specified buffers.
        Zero-pointers can be specified to get the buffers allocated within
        DGILib. This requires the data to be fetched using
        auxiliary_power_copy_data.

        `int auxiliary_power_register_buffer_pointers(uint32_t power_hndl,
        float* buffer, double* timestamp, size_t*
        count, size_t max_count, int channel, int type)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        | *buffer* | Buffer that will hold the samples. Set to 0 for
        automatically allocated. |
        | *timestamp* | Buffer that will hold the timestamp for the samples.
        Set to 0 for automatically allocated. |
        | *count* | Pointer to a variable that will hold the count of samples.
        Set to 0 for automatically allocated. |
        | *max_count* | Number of samples that can fit into the specified
        buffers. Or size of automatically allocated buffers. |
        | *channel* | Power channel for this buffer: A = 0, B = 1 (Power
        Debugger specific) |
        | *type* | Type of power data: Current = 0, Voltage = 1, Range = 2 |
        +------------+------------+

        :param channel: Power channel for this buffer: A = 0, B = 1 (defaults
            to 0)
        :type channel: int
        :param power_type: Type of power data: Current = 0, Voltage = 1,
            Range = 2 (defaults to 0)
        :type power_type: int
        :param max_count: Number of samples that can fit into the specified
            buffers (defaults to BUFFER_SIZE)
        :type max_count: int
        :raises: :exc:`DeviceReturnError`
        """
        self.powerBuffer = (c_float * max_count)()
        self.powerTimestamp = (c_double * max_count)()
        self.powerCount = c_size_t()

        max_count = c_size_t(max_count)
        channel = c_int(channel)
        power_type = c_int(power_type)

        res = self.dgilib.auxiliary_power_register_buffer_pointers(
            self.power_hndl,
            byref(self.powerBuffer),
            byref(self.powerTimestamp),
            byref(self.powerCount),
            max_count,
            channel,
            power_type,
        )
        if self.verbose:
            print(f"\t{res} auxiliary_power_register_buffer_pointers")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_register_buffer_pointers returned: {res}"
            )

    def auxiliary_power_unregister_buffer_pointers(
            self, channel=0, power_type=0):
        """`auxiliary_power_unregister_buffer_pointers`.

        Unregisters the pointers for the specified power channel.

        `int auxiliary_power_unregister_buffer_pointers(uint32_t power_hndl,
        int channel, int type)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        | *channel* | Power channel for this buffer: A = 0, B = 1 (Power
        Debugger specific) |
        | *type* | Type of power data: Current = 0, Voltage = 1, Range = 2 |
        +------------+------------+

        :param channel: Power channel for this buffer: A = 0, B = 1 (defaults
            to 0)
        :type channel: int
        :param power_type: Type of power data: Current = 0, Voltage = 1,
            Range = 2 (defaults to 0)
        :type power_type: int
        :raises: :exc:`DeviceReturnError`
        """
        channel = c_int(channel)
        power_type = c_int(power_type)

        res = self.dgilib.auxiliary_power_unregister_buffer_pointers(
            self.power_hndl, channel, power_type)
        if self.verbose:
            print(
                f"\t{res} auxiliary_power_unregister_buffer_pointers, channel:"
                f" {channel.value}, power_type: {power_type.value}")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_unregister_buffer_pointers, channel: "
                f"{channel.value}, power_type: {power_type.value} returned: "
                f"{res}")

    def auxiliary_power_calibration_is_valid(self):
        """`auxiliary_power_calibration_is_valid`.

        Checks the status of the stored calibration.

        Returns true if the calibration is valid, false otherwise. Unity gain
        and offset will be used.

        `bool auxiliary_power_calibration_is_valid(uint32_t power_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        +------------+------------+

        :return: True if the calibration is valid, False otherwise
        :rtype: bool
        """
        calibration_is_valid = \
            self.dgilib.auxiliary_power_calibration_is_valid(self.power_hndl)
        if self.verbose:
            print(
                f"auxiliary_power_calibration_is_valid: {calibration_is_valid}"
            )

        return bool(calibration_is_valid)

    def auxiliary_power_trigger_calibration(self, circuit_type=XAM):
        """`auxiliary_power_trigger_calibration`.

        Triggers a calibration of the specified type. This can take some time,
        so use `auxiliary_power_get_status` to check for completion.

        `int auxiliary_power_trigger_calibration(uint32_t power_hndl, int type)
        `

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        | *type* | Type of calibration to trigger. See the DGI documentation
        for details. |
        +------------+------------+

        :param circuit_type: Type of calibration to trigger (defaults to XAM)
        :type circuit_type: int
        :raises: :exc:`DeviceReturnError`
        """
        circuit_type = c_int(circuit_type)
        res = self.dgilib.auxiliary_power_trigger_calibration(
            self.power_hndl, circuit_type)
        if self.verbose:
            print(f"\t{res} auxiliary_power_trigger_calibration")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_trigger_calibration returned: {res}")

    def auxiliary_power_get_calibration(self, length=NUM_CALIBRATION):
        """`auxiliary_power_get_calibration`.

        Gets the raw calibration read from the tool.

        `int auxiliary_power_get_calibration(uint32_t power_hndl, uint8_t*
        data, size_t length)`

        Note: actually returns the number of calibration samples, not an error
        if non-zero. The length argument is not used.

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        | *data* | Buffer that will hold the read raw calibration data |
        | *length* | Number of raw calibration bytes to fetch. See the DGI
        documentation for number of bytes. |
        +------------+------------+

        :param length: Number of raw calibration bytes to fetch. See the DGI
            documentation for number of bytes. (defaults to NUM_CALIBRATION)
        :type length: int
        :return: List of the read raw calibration data
        :rtype: list(int)
        :raises: :exc:`DeviceReturnError`
        """
        data = (c_ubyte * length)()
        length = self.dgilib.auxiliary_power_get_calibration(
            self.power_hndl, byref(data))
        if self.verbose:
            print(f"auxiliary_power_get_calibration: {length}")
        if self.verbose >= 2:
            for i in range(length):
                print(f"\t{i}:\t{data[i]}")

        return data[:length]

    def auxiliary_power_get_circuit_type(self):
        """`auxiliary_power_get_circuit_type`.

        Gets the type of power circuit.

        `int auxiliary_power_get_circuit_type(uint32_t power_hndl, int*
        circuit)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        | *circuit* | Pointer to a variable that will hold the circuit type:
        OLD_XAM = 0x00, XAM = 0x10, PAM = 0x11, UNKNOWN = 0xFF |
        +------------+------------+

        :return: The circuit type: OLD_XAM = 0x00, XAM = 0x10, PAM = 0x11,
            UNKNOWN = 0xFF
        :rtype: int
        :raises: :exc:`DeviceReturnError`
        """
        circuit = c_int()
        res = self.dgilib.auxiliary_power_get_circuit_type(
            self.power_hndl, byref(circuit))
        if self.verbose:
            print(f"\t{res} auxiliary_power_get_circuit_type: {circuit.value}")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_get_circuit_type: {circuit.value} returned: "
                f"{res}")

        return circuit.value

    def auxiliary_power_get_status(self):
        """`auxiliary_power_get_status`.

        Gets the status of the power parser.

        Return codes:
        - `IDLE` = 0x00
        - `RUNNING` = 0x01
        - `DONE` = 0x02
        - `CALIBRATING` = 0x03
        - `INIT_FAILED` = 0x10
        - `OVERFLOWED` = 0x11
        - `USB_DISCONNECTED` = 0x12
        - `CALIBRATION_FAILED` = 0x20

        `int auxiliary_power_get_status(uint32_t power_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        +------------+------------+

        :return: The status of the power parser:
            - `IDLE` = 0x00
            - `RUNNING` = 0x01
            - `DONE` = 0x02
            - `CALIBRATING` = 0x03
            - `INIT_FAILED` = 0x10
            - `OVERFLOWED` = 0x11
            - `USB_DISCONNECTED` = 0x12
            - `CALIBRATION_FAILED` = 0x20
        :rtype: int
        """
        status = self.dgilib.auxiliary_power_get_status(
            self.power_hndl)
        if self.verbose:
            print(f"power_status: {status}")

        return status

    def auxiliary_power_start(self, mode=0, parameter=0):
        """`auxiliary_power_start`.

        Starts parsing of power data. The power and power sync interfaces are
        enabled automatically, but note that it is necessary to start the
        polling separately. This only starts the parser that consumes data
        from the DGILib buffer.

        `int auxiliary_power_start(uint32_t power_hndl, int mode, int
        parameter)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        | *mode* | Sets the mode of capture. |
        |  | 0 - continuous capturing which requires the user to periodically
        consume the data. |
        |  | 1 - oneshot capturing that captures data until the buffer has
        been read once, has been filled or the time from the first received
        sample in seconds equals the specified parameter. |
        | *parameter* | Mode specific |
        +------------+------------+

        :param mode: Sets the mode of capture (defaults to 0)
            - 0: continuous capturing which requires the user to periodically
                consume the data
            - 1: oneshot capturing that captures data until the buffer has
            been read once, has been filled or the time from the first
                received sample in seconds equals the specified parameter
        :type mode: int
        :param parameter: Mode specific (defaults to 0)
        :type parameter: int or None
        :raises: :exc:`DeviceReturnError`
        """
        mode = c_int(mode)
        parameter = c_int(parameter)
        res = self.dgilib.auxiliary_power_start(
            self.power_hndl, mode, parameter)
        if self.verbose:
            print(
                f"\t{res} auxiliary_power_start, mode: {mode.value}, "
                f"parameter: {parameter.value}")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_start, mode: {mode.value}, parameter: "
                f"{parameter.value} returned: {res}")

    def auxiliary_power_stop(self):
        """`auxiliary_power_stop`.

        Stops parsing of power data.

        `int auxiliary_power_stop(uint32_t power_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        +------------+------------+

        :raises: :exc:`DeviceReturnError`
        """
        res = self.dgilib.auxiliary_power_stop(
            self.power_hndl)
        if self.verbose:
            print(f"\t{res} auxiliary_power_stop")
        if res:
            raise DeviceReturnError(f"auxiliary_power_stop returned: {res}")

    def auxiliary_power_lock_data_for_reading(self):
        """`auxiliary_power_lock_data_for_reading`.

        Blocks the parsing thread from accessing all the buffers. This must be
        called before the user application code accesses the buffers, or a
        call to `auxiliary_power_copy_data` is made. Afterwards
        `auxiliary_power_free_data` must be called. Minimize the amount of
        time between locking and freeing to avoid buffer overflows.

        `int auxiliary_power_lock_data_for_reading(uint32_t power_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        +------------+------------+

        :raises: :exc:`DeviceReturnError`
        """
        res = self.dgilib.auxiliary_power_lock_data_for_reading(
            self.power_hndl)
        if self.verbose:
            print(f"\t{res} auxiliary_power_lock_data_for_reading")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_lock_data_for_reading returned: {res}")

    def auxiliary_power_copy_data(
            self, channel=0, power_type=0, max_count=BUFFER_SIZE):
        """`auxiliary_power_copy_data`.

        Copies parsed power data into the specified buffer. Remember to lock
        the buffers first. If the count parameter is the same as max_count
        there is probably more data to be read. Do another read to get the
        remaining data.

        `int auxiliary_power_copy_data(uint32_t power_hndl, float* buffer,
        double* timestamp, size_t* count, size_t max_count, int channel, int
        type)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        | *buffer* | Buffer that will hold the samples. |
        | *timestamp* | Buffer that will hold the timestamp for the samples. |
        | *count* | Pointer to a variable that will hold the count of elements
        copied |
        | *max_count* | Maximum number of elements that the buffer can hold |
        | *channel* | Power channel for this buffer: A = 0, B = 1 (Power
        Debugger specific) |
        | *type* | Type of power data: Current = 0, Voltage = 1, Range = 2 |
        +------------+------------+

        :param channel: Power channel for this buffer: A = 0, B = 1 (defaults
            to 0)
        :type channel: int
        :param power_type: Type of power data: Current = 0, Voltage = 1,
            Range = 2 (defaults to 0)
        :type power_type: int
        :param max_count: Maximum number of elements that the buffer can hold
            (defaults to BUFFER_SIZE)
        :type max_count: int
        :return: Tuple of a list of samples and a list of the timestamps for
            the samples
        :rtype: tuple(list(int), list(int))
        :raises: :exc:`DeviceReturnError`
        """
        # buffer = (c_float * max_count)()
        # timestamp = (c_double * max_count)()
        count = c_size_t()
        max_count = c_size_t(max_count)
        channel = c_int(channel)
        power_type = c_int(power_type)

        res = self.dgilib.auxiliary_power_copy_data(
            self.power_hndl,
            self.powerBuffer,
            self.powerTimestamp,
            # byref(self.powerCount),
            # buffer,
            # timestamp,
            byref(count),
            max_count,
            channel,
            power_type,
        )
        if self.verbose:
            print(
                f"\t{res} auxiliary_power_copy_data: {count.value} samples, "
                f"power_type: {power_type.value}")
            # f"\t{res} auxiliary_power_copy_data: {self.powerCount.value} "
            # f"samples, power_type: {power_type.value}"
            if self.verbose >= 3:
                for i in range(min(count.value, MAX_PRINT)):
                    # for i in range(min(self.powerCount.value, MAX_PRINT)):
                    #     print(f"\t{i}: buffer: {buffer[i]}, timestamp: "
                    #         f"{timestamp[i]}")
                    print(
                        f"\t{i}: buffer: {self.powerBuffer[i]}, timestamp: "
                        f"{self.powerTimestamp[i]}")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_copy_data returned: {res}")

        return (self.powerTimestamp[: count.value],
                self.powerBuffer[:count.value])
        # return (self.powerTimestamp[: self.powerCount.value],
        #         self.powerBuffer[:self.powerCount.value])
        # return timestamp[:], buffer[:]

    def auxiliary_power_free_data(self):
        """`auxiliary_power_free_data`.

        Clears the power data buffers and allows the power parser to continue.

        `int auxiliary_power_free_data(uint32_t power_hndl)`

        +------------+------------+
        | Parameter  | Description |
        +============+============+
        | *power_hndl* | Handle of the power parser |
        +------------+------------+

        :raises: :exc:`DeviceReturnError`
        """
        res = self.dgilib.auxiliary_power_free_data(
            self.power_hndl)
        if self.verbose:
            print(f"\t{res} auxiliary_power_free_data")
        if res:
            raise DeviceReturnError(
                f"auxiliary_power_free_data returned: {res}")
