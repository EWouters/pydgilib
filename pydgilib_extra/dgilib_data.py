"""This module provides classes to store DGILib Logger Interface Data."""

from pydgilib.dgilib_config import (
    INTERFACE_GPIO)
from pydgilib_extra.dgilib_extra_config import (INTERFACES, INTERFACE_POWER)


class InterfaceData(object):
    """Class to store DGILib Logger Interface Data."""

    __slots__ = ['timestamps', 'values']

    def __init__(self, *args):
        """Take tuple of timestamps and values."""
        if (not args):
            self.timestamps = []
            self.values = []
        elif (len(args) == 1 and isinstance(args[0], InterfaceData)):
            self = args[0]
        elif (len(args) == 1 and valid_interface_data(args[0])):
            self.timestamps, self.values = args[0]
        elif (len(args) == 2 and isinstance(args[0], list) and
              isinstance(args[1], list)):
            self.timestamps, self.values = args
        elif (len(args) == 2 and isinstance(args[0], (int, float)) and
              isinstance(args[1], (int, float, list))):
            self.timestamps = [args[0]]
            self.values = [args[1]]
        else:
            raise ValueError(
                f"Samples passed to InterfaceData must be tuple([],[]) or "
                "timestamps, values or InterfaceData. Got {args}")

    def __iadd__(self, interface_data):
        """Append new interface_data (in-place).

        Used to provide `interface_data += interface_data1` syntax
        """
        if isinstance(interface_data, InterfaceData):
            self.timestamps.extend(interface_data.timestamps)
            self.values.extend(interface_data.values)
        else:
            assert valid_interface_data(
                interface_data), f"Samples passed to InterfaceData were not " \
                "valid_interface_data. {interface_data}"
            if isinstance(interface_data[0], list):
                self.timestamps.extend(interface_data[0])
                self.values.extend(interface_data[1])
            else:
                self.timestamps.extend([interface_data[0]])
                self.values.extend([interface_data[1]])
        return self

    def __add__(self, interface_data):
        """Append new interface_data (copy).

        Used to provide `interface_data2 = interface_data1 + interface_data`
        syntax
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
        if len(self.timestamps):
            return len(self.timestamps)
        else:
            return 0

    def __getitem__(self, index):
        """Get item.

        Used to provide `timestamp, value = interface_data[5]` and
        `timestamp, value = interface_data[2:5]` syntax
        """
        return (self.timestamps[index], self.values[index])

    def __contains__(self, item):
        """Contains.

        Used to provide `([1], [2]) in interface_data` syntax
        """
        return all(any(item_timestamp == self_timestamp and
                       item_value == self_value
                       for self_timestamp, self_value in self)
                   for item_timestamp, item_value in (
                       item if isinstance(item, InterfaceData) else
                       InterfaceData(item)))

    def __str__(self):
        """Print data.

        Used to provide `str(data)` syntax.
        """
        return str(tuple(self))

    def get_select_in_value(self, begin=0, end=None, start_time=None,
                            end_time=None):
        """
        get_select_in_value.

        Use to slice a items in the values when the values are iterables.

        Keyword Arguments:
            begin {int} -- Begin index of item in value (default: {0})
            end {[type]} -- End index of item in value, if not supplied only
                the item the begin index will be returned (default: {None})
            start_time {[type]} -- Start time of selection (default: {None})
            end_time {[type]} -- End time of selection (default: {None})

        Returns:
            [list] -- List of values that have timestamps between start_time
                and end_time
        """

        if start_time is None and end_time is None:
            return [value[begin] for value in self.values] if end is None \
                else [value[begin:end] for value in self.values]

        start_index = 0
        end_index = len(self.timestamps) - 1
        # Get the index of the first sample after the start_time
        if start_time is not None:
            start_index = self.get_index(start_time)
        if end_time is not None:
            end_index = self.get_index(end_time, start_index)

        return [value[begin] for value in self.values[start_index:end_index]] \
            if end is None else \
            [value[begin:end] for value in self.values[start_index:end_index]]

    def get_index(self, timestamp, start_index=0):
        """Get the index of the first sample after the timestamp."""
        index = start_index  # Start at start_index (can speed up search)
        max_index = len(self) - 1
        while index < max_index and self.timestamps[index] < timestamp:
            index += 1
        return index

    def get_next_available_timestamps(self, timestamp_to_compare, start_index=0):
        index = self.get_index(timestamp_to_compare, start_index)

        if self.timestamps[index] >= timestamp_to_compare:
            if index == 0:
                return (None, self.timestamps[index], None, index)
            else:
                return (self.timestamps[index-1], self.timestamps[index], index-1, index)
        else:
            return (None, None, None, None)


class LoggerData(dict):
    """Class to store DGILib Logger Data."""

    # __slots__ = [INTERFACE_GPIO, INTERFACE_POWER]

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
        return self[INTERFACES[attr]]

    def __setattr__(self, attr, value):
        """Set attribute.

        Used to provide `data.spi = InterfaceData(([], []))` syntax.
        """
        self[INTERFACES[attr]] = value

    def __iadd__(self, logger_data):
        """Append new logger_data (in-place).

        Used to provide `logger_data1 += logger_data` syntax
        """
        if not isinstance(logger_data, dict):
            raise ValueError(
                f"logger_data must be a dict or LoggerData. "
                "Got {type(logger_data)}")
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
            return {key: len(interface_data)
                    for key, interface_data in self.items()}
        elif attr in self.keys():
            return len(self[attr])
        elif attr in INTERFACES.keys():
            return len(self[INTERFACES[attr]])
        else:
            raise ValueError(
                f"attr must be a named or numbered interface. Got {attr}")

    def __str__(self):
        """Print data.

        Used to provide `str(data)` syntax.
        """
        output = "Interfaces:\n"
        for interface in self.keys():
            if interface in INTERFACES.values():
                for name, number in INTERFACES.items():
                    if interface == number:
                        output += f"\t{number:4}: {name + ',':{' '}^{10}} samples: {len(self[interface]):7}\n"
                        break
            else:
                output += f"\t{interface:4}: (unknown),  samples: {len(self[interface]):7}\n"

        return output

# # Load CSV

# # Calculations


def valid_interface_data(samples):
    """Check if samples are valid InterfaceData."""
    return (isinstance(samples, (tuple, list)) and
            len(samples) == 2 and
            all(isinstance(sample, (list, float, int)) for sample in samples) and
            (isinstance(samples[0], float) or len(samples[0]) == len(samples[1])))
