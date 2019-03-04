"""This module provides a base interface class."""


class DGILibInterface(object):
    """Provides a base interface class."""

    def __init__(self, *args, **kwargs):
        """Instantiate DGILibInterfacePower object."""
        # Argument parsing
        self.power_buffers = kwargs.get("power_buffers", [])
        if self.pydgilib.verbose:
            print("power_buffers: ", self.power_buffers)

    def __enter__(self):
        """For usage in `with DGILibExtra() as dgilib:` syntax."""
        # Check if calibration is valid and trigger calibration if it is not
        self.circuit_type = self.auxiliary_power_get_circuit_type()
        if not self.auxiliary_power_calibration_is_valid():
            self.auxiliary_power_trigger_calibration(self.circuit_type)

        # Register buffers inside the library for the buffers specified in
        # self.power_buffers
        for power_buffer in self.power_buffers:
            self.auxiliary_power_register_buffer_pointers(
                channel=power_buffer["channel"],
                power_type=power_buffer["power_type"])

        self.power_set_config(self.power_buffers)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """For usage in `with DGILibExtra() as dgilib:` syntax."""
        self.power_set_config([])  # Disables the interface

    def auxiliary_power_calibration(self, circuit_type=XAM):
        """Calibrate the Auxiliary Power interface of the device.

        :param circuit_type: Type of calibration to trigger (defaults to XAM)
        :type circuit_type: int
        """
        self.auxiliary_power_trigger_calibration(circuit_type)
        while self.auxiliary_power_get_status() == CALIBRATING:
            sleep(0.1)

    def power_get_config(self):
        """Get the power config options.

        :return: Power buffers configuration list of dictionaries like
            `[{"channel": CHANNEL_A, "power_type": POWER_CURRENT}]`
        :rtype: list(dict())
        """
        # Return the configuration
        return self.power_buffers

    def power_set_config(self, power_buffers):
        """Set the power config options.

        Register buffers inside the library for the buffers specified in
        power_buffers and removes ones that are not present.

        :param power_buffers: Power buffers configuration list of dictionaries
            like `[{"channel": CHANNEL_A, "power_type": POWER_CURRENT}]`
        :type power_buffers: list(dict())
        """
        # Disable the configurations that are not in the new config and remove
        # them from self.power_buffers
        for power_buffer in self.power_buffers:
            if power_buffer not in power_buffers:
                self.auxiliary_power_unregister_buffer_pointers(
                    channel=power_buffer["channel"],
                    power_type=power_buffer["power_type"],
                )
                self.power_buffers.remove(power_buffer)

        # Enable the configurations that are in the new config and not in
        # self.power_buffers
        for power_buffer in power_buffers:
            if power_buffer not in self.power_buffers:
                self.auxiliary_power_register_buffer_pointers(
                    channel=power_buffer["channel"],
                    power_type=power_buffer["power_type"],
                )
                self.power_buffers.append(power_buffer)

        if (self.power_buffers and
                INTERFACE_POWER not in self.enabled_interfaces):
            self.enabled_interfaces.append(INTERFACE_POWER)
        if (not self.power_buffers and
                INTERFACE_POWER in self.enabled_interfaces):
            self.enabled_interfaces.remove(INTERFACE_POWER)

    def power_read_buffer(self, power_buffer, *args, **kwargs):
        """Read power data of the specified buffer.

        TODO: Copies parsed power data into the specified buffer. Remember to
        lock the buffers first. If the count parameter is the same as
        max_count there is probably more data to be read. Do another read to
        get the remaining data.

        :return: TODOTODO Tuple of list of power samples in Ampere and list of
            timestamps in seconds
        :rtype: (list(float), list(float))
        """
        # Check if power_buffer is in self.power_buffers
        if power_buffer not in self.power_buffers:
            raise PowerReadError(
                f"Power Buffer {power_buffer} does not exist in "
                f"self.power_buffers: {self.power_buffers}.")

        # Check if auxiliary_power_get_status() is in
        #   - IDLE = 0x00,
        #   - RUNNING = 0x01,
        #   - DONE = 0x02 or
        #   - OVERFLOWED = 0x11
        # and raise PowerStatusError if it is.
        power_status = self.auxiliary_power_get_status()
        if self.pydgilib.verbose:
            print(f"power_status: {power_status}")
        # if power_status <= DONE or power_status == OVERFLOWED:
        if power_status not in (IDLE, RUNNING, DONE, OVERFLOWED):
            raise PowerStatusError(f"Power Status {power_status}.")
        if power_status == OVERFLOWED:
            print(
                f"BUFFER OVERFLOW, call this function more frequently or "
                f"increase the buffer size.")

        # Create variables to the store data in
        power_samples = []
        timestamps = []

        # TODO: Check implementation in case of buffer overflow.
        # Should auxiliary_power_lock_data_for_reading() be inside the loop
        # or before?

        # Get the data from the buffer in the library
        while True:
            self.auxiliary_power_lock_data_for_reading()
            _power_samples, _timestamps = self.auxiliary_power_copy_data(
                power_buffer["channel"],
                power_buffer["power_type"],
                *args,
                **kwargs,
            )
            # BUG: This probably clears all channels! (channels might not be
            # working on XAM anyway)
            self.auxiliary_power_free_data()
            power_samples.extend(_power_samples)
            timestamps.extend(_timestamps)
            # Repeat the loop until there is no buffer overflow (which should
            # always be avoided.)
            if self.auxiliary_power_get_status() != OVERFLOWED:
                break

        if self.pydgilib.verbose >= 2:
            print(f"Collected {len(power_samples)} power samples")
        if self.pydgilib.verbose >= 4:
            print(timestamps, power_samples)

        return timestamps, power_samples

#     def power_read(self, *args, **kwargs):
#         """Read power data from all enabled buffers.

#         The returned list has the same indexes as the list obtained from
#         `power_get_config()`
#         """
