"""Class to store DGILib Logger Data."""

from pydgilib_extra.dgilib_extra_config import (
    INTERFACE_SPI, INTERFACE_USART, INTERFACE_I2C, INTERFACE_GPIO,
    INTERFACE_POWER)

attr_dict = {
    "spi": INTERFACE_SPI,
    "usart": INTERFACE_USART,
    "i2c": INTERFACE_I2C,
    "gpio": INTERFACE_GPIO,
    "power": INTERFACE_POWER,
}


class InterfaceData(tuple):
    """Class to store DGILib Logger Interface Data."""

    def __new__(*args, **kwargs):
        """Take tuple of timestamps and values."""
        # Call init function of tuple
        if len(args) == 1:
            args = *args, ([], [])
        assert valid_interface_data(
            args[1]), f"Samples passed to InterfaceData were not valid_interface_data. {args[1]}"
        return tuple.__new__(*args, **kwargs)

    @property
    def timestamps(self):
        """Get the list of timestamps."""
        return self[0]

    @property
    def values(self):
        """Get the list of values."""
        return self[1]

    def __iadd__(self, interface_data):
        """Append new interface_data (in-place).

        Used to provide `interface_data += interface_data1` syntax
        """
        if not isinstance(interface_data, InterfaceData):
            assert valid_interface_data(
                interface_data), f"Samples passed to InterfaceData were not valid_interface_data. {interface_data}"
        self[0].extend(interface_data[0])
        self[1].extend(interface_data[1])
        return self

    def __add__(self, interface_data):
        """Append new interface_data (copy).

        Used to provide `interface_data2 = interface_data1 + interface_data` syntax
        """
        data = InterfaceData()
        data += self
        data += interface_data
        return data

    def append(self, interface_data):
        """Append interface_data."""
        return self.extend(interface_data)

    def extend(self, interface_data):
        """Append a list of interface_data."""
        if isinstance(interface_data, InterfaceData):
            self += interface_data
        else:
            self += InterfaceData(interface_data)
        return self

    def __len__(self):
        """Get the number of samples."""
        return len(self[0])


class LoggerData(dict):
    """Class to store DGILib Logger Data."""

    def __init__(self, *args, **kwargs):
        """Take list of interfaces for the data."""
        # Call init function of dict
        super().__init__(self)
        # No args or kwargs were specified, populate args[0] with standard
        # interfaces
        if not args and not kwargs:
            args = [[INTERFACE_GPIO, INTERFACE_POWER]]
        # Args is list of interfaces, make data dict with interfaces as keys
        # and tuples of lists as values
        if args and isinstance(args[0], list):
            for interface in args[0]:
                self[interface] = InterfaceData()
        # Instantiate dict with arguments
        else:
            self.update(*args, **kwargs)

        for interface, interface_data in self.items():
            if not isinstance(interface_data, InterfaceData):
                self[interface] = InterfaceData(interface_data)

    def __getattr__(self, attr):
        """Get attribute.

        Used to provide `data.spi` syntax.
        """
        return self[attr_dict[attr]]

    def __setattr__(self, attr, value):
        """Set attribute.

        Used to provide `data.spi = InterfaceData(([], []))` syntax.
        """
        self[attr_dict[attr]] = value

    def __iadd__(self, logger_data):
        """Append new logger_data (in-place).

        Used to provide `logger_data1 += logger_data` syntax
        """
        if not isinstance(logger_data, dict):
            raise ValueError(
                f"logger_data must be a dict or LoggerData. Got {type(logger_data)}")
        for interface, interface_data in logger_data.items():
            self.extend(interface, interface_data)
        return self

    def __add__(self, logger_data):
        """Append new logger_data (copy).

        Used to provide `logger_data2 = logger_data1 + logger_data` syntax
        """
        data = LoggerData()
        data += self
        data += logger_data
        return data

    # def __copy__(self):
    #     return self

    def append(self, interface, interface_data):
        """Append a sample to one of the interfaces."""
        return self.extend(interface, interface_data)

    def extend(self, interface, interface_data):
        """Append a list of samples to one of the interfaces."""
        if interface in self.keys():
            self[interface].extend(interface_data)
        elif not isinstance(interface_data, InterfaceData):
            self[interface] = InterfaceData(interface_data)
        else:
            self[interface] = interface_data
        return self

    def length(self, attr=None):
        """Compute the number of samples for the interfaces.

        Return a dict of the number of samples for each interface. Or the
        length of the `attr` specified.
        """
        if attr is None:
            return {key: len(interface_data) for key, interface_data in self.items()}
        elif attr in self.keys():
            return len(self[attr])
        elif attr in attr_dict.keys():
            return len(self[attr_dict[attr]])
        else:
            raise ValueError(
                f"attr must be a named or numbered interface. Got {attr}")

    def __repr__(self):
        """Print data.

        Used to provide `str(data)` syntax.
        """
        output = "Interfaces:\n"
        for interface in self.keys():
            if interface in attr_dict.values():
                for name, number in attr_dict.items():
                    if interface == number:
                        output += f"\t{number:4}: {name:{' '}^{10}}, samples: {len(self[interface][0]):7}\n"
                        break
            else:
                output += f"\t{interface:4}: (unknown) , samples: {len(self[interface][0]):7}\n"

        return output

# # Load CSV

# # Calculations


def valid_interface_data(samples):
    """Check if samples are valid InterfaceData."""
    return (isinstance(samples, (tuple, list)) and
            len(samples) == 2 and
            all(isinstance(sample, list) for sample in samples) and
            len(samples[0]) == len(samples[1]))
