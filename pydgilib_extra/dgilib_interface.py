"""This module provides a base interface class."""

from os import (path, getcwd)
import csv
import warnings

from pydgilib_extra.dgilib_data import InterfaceData
from pydgilib_extra.dgilib_extra_exceptions import InterfaceNotAvailableError
from pydgilib_extra.dgilib_extra_config import POLLING


class DGILibInterface(object):
    """Provides a base interface class."""

    interface_id = -1
    name = "interface_name"
    csv_header = ["timestamp", "value"]
    file_name_base = "log"
    polling_type = POLLING

    @staticmethod
    def _csv_reader_map(row): return (float(row[0]), float(row[1]))

    def __init__(self, *args, **kwargs):
        """Instantiate DGILibInterfaceGPIO object."""
        self.file_handle = None
        self.csv_writer = None
        # Argument parsing
        self.dgilib_extra = kwargs.get(
            "dgilib_extra", args[0] if args else None)
        self.verbose = kwargs.get("verbose", 0)
        self.file_name_base = kwargs.get("file_name_base", self.file_name_base)
        # Set interface configuration
        if self.dgilib_extra is not None:
            self.set_config(*args, **kwargs)

    def get_config(self):
        """Get configuration options.

        :return: Configuration dictionary
        :rtype: dict()
        """
        # Return the configuration
        return None

    def set_config(self, *args, **kwargs):
        """Set configuration options."""
        pass

    def enable(self):
        """Enable the interface."""
        if self.interface_id not in self.dgilib_extra.available_interfaces:
            raise InterfaceNotAvailableError(
                f"Interface {self.interface_id} not available. Available interfaces: {self.dgilib_extra.available_interfaces}")
        if self.interface_id not in self.dgilib_extra.enabled_interfaces:
            self.dgilib_extra.interface_enable(self.interface_id)
            self.dgilib_extra.enabled_interfaces.append(self.interface_id)

    def disable(self):
        """Disable the interface."""
        if self.interface_id in self.dgilib_extra.enabled_interfaces:
            self.dgilib_extra.interface_disable(self.interface_id)
            self.dgilib_extra.enabled_interfaces.remove(self.interface_id)

    def read(self, *args, **kwargs):
        """Read data from the interface.

        :return: Interface data
        :rtype: InterfaceData
        """
        # Return the data
        return None

    def write(self, *args, **kwargs):
        """Read data from the interface."""
        pass

    def init_csv_writer(
            self, log_folder=getcwd(), file_name_base="log", newline='',
            mode='w'):
        """init_csv_writer."""
        # Open file handle
        self.file_handle = open(path.join(
            log_folder, (file_name_base + '_' + self.name + ".csv")),
            mode, newline=newline)
        # Create csv.writer
        self.csv_writer = csv.writer(self.file_handle)
        # Write header to file
        self.csv_writer.writerow(self.csv_header)

    def close_csv_writer(self):
        """close_csv_writer."""
        # Close file handle
        self.file_handle.close()

    def csv_write_rows(self, interdace_data):
        """csv_write_rows."""
        self.csv_writer.writerows(interdace_data)

    def csv_read_file(self, file_path=None, newline='', mode='r'):
        """csv_read_file."""
        if file_path is None:
            file_path = path.join(
                getcwd(), (self.file_name_base + '_' + self.name + ".csv"))
        with open(path.join(file_path), mode, newline=newline) as csv_file:
            interface_data = InterfaceData()
            reader = csv.reader(csv_file)
            header = next(reader)
            if header != self.csv_header:
                warnings.warn(
                    f"Header of .csv file did not match expected value. Got "
                    f"{header}, expected {self.csv_header}, file: "
                    f"{path.join(file_path)}.")
            for row in reader:
                interface_data += self._csv_reader_map(row)
            return interface_data
