"""This module wraps the calls to the GPIO interface."""

from pydgilib_extra.dgilib_extra_config import (INTERFACE_GPIO, NUM_PINS)
from pydgilib_extra.dgilib_interface import DGILibInterface
from pydgilib_extra.dgilib_data import InterfaceData


# TODO: make these functions faster/better?
def int2bool(i):
    """Convert int to list of bool."""
    return [bit is "1" for bit in f"{i:04b}"]  # Note: NUM_PINS is hardcoded here


def bool2int(b):
    """Convert list of bool to int."""
    return int("".join("1" if d else "0" for d in b), 2)


class DGILibInterfaceGPIO(DGILibInterface):
    """Wraps the calls to the GPIO interface."""

    name = "gpio"
    csv_header = ["timestamp"] + [f"gpio{n}" for n in range(NUM_PINS)]

    def __init__(self, *args, **kwargs):
        """Instantiate DGILibInterfaceGPIO object."""
        # Set default values for attributes
        self.read_mode = [False] * 4
        self.write_mode = [False] * 4
        # Instantiate base class
        DGILibInterface.__init__(self, *args, **kwargs)
        # Parse arguments
        self.augment_gpio = kwargs.get("augment_gpio", None)
        self.gpio_delay_time = kwargs.get("gpio_delay_time", 0)
        self.gpio_switch_time = kwargs.get("gpio_switch_time", 0)
        # If augment_gpio was not specified set it to true if gpio_delay_time
        # or gpio_switch_time was non 0.
        if self.augment_gpio is None:
            self.augment_gpio = (
                self.gpio_delay_time != 0 or self.gpio_switch_time != 0)

        if self.dgilib_extra.timer_factor is None:
            self.dgilib_extra.timer_factor = self.dgilib_extra.get_time_factor()

        if self.verbose:
            print("read_mode: ", self.read_mode)
            print("write_mode: ", self.write_mode)
            print("augment_gpio: ", self.augment_gpio)
            if self.augment_gpio:
                print("gpio_delay_time: ", self.gpio_delay_time)
                print("gpio_switch_time: ", self.gpio_switch_time)

    def get_config(self):
        """Get the pin-mode for the GPIO pins.

        The GPIO configuration controls the direction of the pins.

        Input pins:  Setting a bit to 1 means the pin is monitored.
        Output pins: Setting a bit to 1 means the pin is set to output and can
        be controlled by the send command.

        :return: Tuple of:
            - List of read modes, Setting a pin to True means the pin is
                monitored.
            - List of write modes, Setting a pin to True means the pin is set
                to output and can be controlled by the send command.
        :rtype: (list(bool), list(bool))
        """
        # Get the configuration
        _, config_value = self.dgilib_extra.interface_get_configuration(
            INTERFACE_GPIO)

        # Convert int to lists of bool
        read_mode = int2bool(config_value[0])
        write_mode = int2bool(config_value[1])

        return read_mode, write_mode

#     def set_config(self, read_mode=[False] * 4, write_mode=[False] * 4):

#         # Update internal values
#         self.read_mode = read_mode
#         self.write_mode = write_mode

    def set_config(self, *args, **kwargs):
        """Set the pin-mode for the GPIO pins.

        The GPIO configuration controls the direction of the pins, and enables
        the interface if needed.

        Input pins:  Setting a bit to 1 means the pin is monitored.
        Output pins: Setting a bit to 1 means the pin is set to output and can
        be controlled by the send command.

        If any of the pins are set to read mode or write mode the GPIO
        interface will be enabled. If none of the pins are set to read mode or
        write mode the GPIO interface will be disabled.

        :param read_mode: List of modes, Setting a pin to True means the pin
            is monitored.
        :type read_mode: list(bool)
        :param write_mode: List of modes, Setting a pin to True means the pin
            is set to output and can be controlled by the send command.
        :type write_mode: list(bool)
        """
        # Argument parsing
        self.read_mode = kwargs.get("read_mode", self.read_mode)
        self.write_mode = kwargs.get("write_mode", self.write_mode)

        # Convert lists of bool to int
        read_mode = bool2int(self.read_mode)
        write_mode = bool2int(self.write_mode)

        # Set the configuration
        if "read_mode" in kwargs:
            self.dgilib_extra.interface_set_configuration(
                INTERFACE_GPIO, [0], [read_mode])
        if "write_mode" in kwargs:
            self.dgilib_extra.interface_set_configuration(
                INTERFACE_GPIO, [1], [write_mode])

    def read(self):
        """Get the state of the GPIO pins.

        Clears the buffer and returns the values.

        :return: Tuple of list of timestamps in seconds and list of list of
            pin states (bool)
        :rtype: (list(float), list(list(bool)))
        """
        # Read the data from the buffer
        pin_values, ticks = self.dgilib_extra.interface_read_data(
            INTERFACE_GPIO)

        pin_values = [int2bool(pin_value) for pin_value in pin_values]
        timestamps = [tick * self.dgilib_extra.timer_factor for tick in ticks]

        if self.verbose >= 2:
            print(
                f"Collected {len(pin_values)} gpio samples (4 pins per sample)"
            )

        return InterfaceData(timestamps, pin_values)

    def write(self, pin_values):
        """Set the state of the GPIO pins.

        Make sure to set the pin to write mode first. Possibly also needs to
        be configured properly on the board

        A maximum of 255 elements can be written each time. An error return
        code will be given if data hasn’t been written yet.

        :param pin_values: List of pin values. Has to include all four pins ?
            TODO: TEST
        :type pin_values: list(bool)
        """
        # Convert list of bool to int
        pin_values = bool2int(pin_values)

        self.dgilib_extra.interface_write_data(INTERFACE_GPIO, [pin_values])

        if self.verbose >= 2:
            print(f"Sent gpio packet")

    def csv_write_rows(self, interdace_data):
        """csv_write_rows."""
        self.csv_writer.writerows(
            zip(interdace_data.timestamps,
                *map(iter, zip(*interdace_data.values))))


def gpio_augment_edges(samples, delay_time=0, switch_time=0, extend_to=None):
    """GPIO Augment Edges.

    Augments the edges of the GPIO data by inserting an extra sample of the
    previous pin values at moment before a switch occurs (minus switch_time).
    The switch time is measured to be around 0.3 ms.

    Also delays all time stamps by delay_time. The delay time seems to vary
    a lot between different projects and should be manually specified for the
    best accuracy.

    Can insert the last datapoint again at the time specified (has to be after
    last sample).

    :param samples: Tuple of samples of GPIO data.
    :type samples: tuple(list(int), list(list(bool)))
    :param delay_time: Switch time of GPIO pin.
    :type delay_time: float
    :param switch_time: Switch time of GPIO pin.
    :type switch_time: float
    :param extend_to: Inserts the last pin values again at the time specified
        (only used if time is after last sample).
    :type extend_to: float
    :return: Tuple of samples of GPIO data.
    :rtype: tuple(list(int), list(list(bool)))
    """
    pin_states = [False] * 4

    # iterate over the list and insert items at the same time:
    i = 0
    while i < len(samples[0]):
        if samples[1][i] != pin_states:
            # This inserts a time sample at time + switch time (so moves the
            # time stamp into the future)
            samples[0].insert(i, samples[0][i] - switch_time)
            # This inserts the last datapoint again at the time the next
            # switch actually arrived (without switch time)
            samples[1].insert(i, pin_states)
            i += 1
            pin_states = samples[1][i]
        i += 1

    # Delay all time stamps by delay_time
    samples[0] = [t + delay_time for t in samples[0]]

    if extend_to is not None:
        if extend_to >= samples[0][-1]:
            samples[0].append(extend_to)
            samples[1].append(pin_states)
    return samples
