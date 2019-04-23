"""This module wraps the calls to the GPIO interface."""

from pydgilib.dgilib_config import INTERFACE_GPIO
from pydgilib_extra.dgilib_extra_config import NUM_PINS
from pydgilib_extra.dgilib_interface import DGILibInterface
from pydgilib_extra.dgilib_calculations import GPIOAugmentEdges
from pydgilib_extra.dgilib_data import InterfaceData


# TODO: make these functions faster/better?
def int2bool(i):
    """int2bool

    Convert int to tuple of bool.

    Parameters
    ----------
    i : int
        The `int` value to be converted.
    """
    return tuple(bit is '1' for bit in reversed(bin(i)[2:].zfill(NUM_PINS)))


def bool2int(b):
    """bool2int

    Convert iterable of bool to int.

    Parameters
    ----------
    b : bool
        The `bool` value to be converted.
    """
    return int(''.join('1' if d else '0' for d in reversed(b)), 2)


class DGILibInterfaceGPIO(DGILibInterface):
    """Wraps the calls to the GPIO interface."""

    interface_id = INTERFACE_GPIO
    name = "gpio"
    csv_header = ["timestamp"] + [f"gpio{n}" for n in range(NUM_PINS)]
    default_gpio_delay_time = 0.00075

    @staticmethod
    def _csv_reader_map(row):
        return float(row[0]), [value == "True" for value in row[1:]]

    def __init__(self, *args, **kwargs):
        """Instantiate DGILibInterfaceGPIO object."""
        # Set default values for attributes
        self.read_mode = [True] * NUM_PINS
        self.write_mode = [False] * NUM_PINS
        # Add read and write mode to kwargs so they get set in the super class
        # constructor
        if "read_mode" not in kwargs:
            kwargs["read_mode"] = self.read_mode
        if "write_mode" not in kwargs:
            kwargs["write_mode"] = self.write_mode
        # Instantiate base class
        DGILibInterface.__init__(self, *args, **kwargs)

        # Parse arguments
        # By default augment gpio with delay of self.default_gpio_delay_time
        if kwargs.get("augment_gpio", True) or "gpio_delay_time" in kwargs or \
                "gpio_switch_time" in kwargs:
            self.augment_gpio = True
            self.gpio_delay_time = kwargs.get(
                "gpio_delay_time", self.default_gpio_delay_time)
            self.gpio_switch_time = kwargs.get("gpio_switch_time", 0)
            self.gpio_augment_edges_streaming = GPIOAugmentEdges()
            self.gpio_augment_edges = \
                self.gpio_augment_edges_streaming.gpio_augment_edges

        # NOTE: Might not be the best place to do this
        if self.dgilib_extra is not None and \
                self.dgilib_extra.timer_factor is None:
            self.dgilib_extra.timer_factor = \
                self.dgilib_extra.get_time_factor()

        if self.verbose:
            print("read_mode: ", self.read_mode)
            print("write_mode: ", self.write_mode)
            print("augment_gpio: ", self.augment_gpio)
            if self.augment_gpio:
                print("gpio_delay_time: ", self.gpio_delay_time)
                print("gpio_switch_time: ", self.gpio_switch_time)

    def get_config(self):
        """get_config

        Get the pin-mode for the GPIO pins.

        The GPIO configuration controls the direction of the pins.

        Input pins:  Setting a bit to 1 means the pin is monitored.
        Output pins: Setting a bit to 1 means the pin is set to output and can
        be controlled by the send command.

        Returns
        -------
        tuple(list(bool, bool, bool, bool), list(bool, bool, bool, bool))
            Tuple of:

            * List of read modes, Setting a pin to True means the pin is \
            monitored.

            * List of write modes, Setting a pin to True means the pin is set \
            to output and can be controlled by the send command.
        """
        # Get the configuration
        _, config_value = self.dgilib_extra.interface_get_configuration(
            INTERFACE_GPIO)

        # Convert int to lists of bool
        read_mode = int2bool(config_value[0])
        write_mode = int2bool(config_value[1])

        return read_mode, write_mode

    def set_config(self, *args, **kwargs):
        """set_config

        Set the pin-mode for the GPIO pins.

        The GPIO configuration controls the direction of the pins, and enables
        the interface if needed.

        Input pins:  Setting a bit to 1 means the pin is monitored.
        Output pins: Setting a bit to 1 means the pin is set to output and can
        be controlled by the send command.

        If any of the pins are set to read mode or write mode the GPIO
        interface will be enabled. If none of the pins are set to read mode or
        write mode the GPIO interface will be disabled.

        Parameters
        ----------
        read_mode : list(bool, bool, bool, bool)
            List of modes. Setting a pin to `True` means the pin
            is monitored.

        write_mode : list(bool, bool, bool, bool)
            List of modes. Setting a pin to `True` means the pin
            is set to output and can be controlled by the send command.
        """
        # Set the configuration
        if "read_mode" in kwargs:
            self.read_mode = kwargs["read_mode"]
            self.dgilib_extra.interface_set_configuration(
                INTERFACE_GPIO, [0], [bool2int(self.read_mode)])
        if "write_mode" in kwargs:
            self.write_mode = kwargs["write_mode"]
            self.dgilib_extra.interface_set_configuration(
                INTERFACE_GPIO, [1], [bool2int(self.write_mode)])

    def read(self):
        """read

        Get the state of the GPIO pins.

        Clears the buffer and returns the values.

        Returns
        -------
        tuple(list(float), list(list(bool, bool, bool, bool)))
            Tuple of list of timestamps in seconds and list of list of
            pin states (bool).
        """
        # Read the data from the buffer
        ticks, pin_values = self.dgilib_extra.interface_read_data(
            INTERFACE_GPIO)

        pin_values = [int2bool(pin_value) for pin_value in pin_values]
        timestamps = [tick * self.dgilib_extra.timer_factor for tick in ticks]

        if self.verbose >= 2:
            print(f"Collected {len(pin_values)} gpio samples ({NUM_PINS} " +
                  "pins per sample)")

        if self.augment_gpio:
            interface_data = InterfaceData(timestamps, pin_values)
            self.gpio_augment_edges(
                interface_data, self.gpio_delay_time, self.gpio_switch_time)
            return interface_data
        else:
            return InterfaceData(timestamps, pin_values)

    def write(self, pin_values):
        """write

        Set the state of the GPIO pins.

        Make sure to set the pin to write mode first. Possibly also needs to
        be configured properly on the board

        A maximum of 255 elements can be written each time. An error return
        code will be given if data hasn’t been written yet.

        Parameters
        ----------
        pin_values : list(bool, bool, bool, bool)
            List of pin values. Has to include all four pins.
        """
        # TODO: Test if it has to include all four pins

        # Convert list of bool to int
        pin_values = bool2int(pin_values)

        self.dgilib_extra.interface_write_data(INTERFACE_GPIO, [pin_values])

        if self.verbose >= 2:
            print(f"Sent gpio packet")

    def csv_write_rows(self, interface_data):
        """csv_write_rows

        """
        self.csv_writer.writerows(
            zip(interface_data.timestamps,
                *map(iter, zip(*interface_data.values))))
