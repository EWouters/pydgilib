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
        """Instantiate DGILibInterface object."""
        self.file_handle = None
        self.csv_writer = None
        # Argument parsing
        self.dgilib_extra = kwargs.get(
            "dgilib_extra", args[0] if args else None)
        self.verbose = kwargs.get("verbose", 0)
        if "file_name_base" in kwargs:
            self.file_name_base = kwargs["file_name_base"]
        # Set interface configuration
        if self.dgilib_extra is not None:
            self.set_config(*args, **kwargs)

    def get_config(self):
        """get_config

        Get configuration options.

        Returns
        -------
        dict
            Configuration dictionary
        """
        # Return the configuration
        return None

    def set_config(self, *args, **kwargs):
        """Set configuration options."""
        pass

    def enable(self):
        """enable

        Enable the interface.
        """
        if self.interface_id not in self.dgilib_extra.available_interfaces:
            raise InterfaceNotAvailableError(
                f"Interface {self.interface_id} not available. Available " +
                f"interfaces: {self.dgilib_extra.available_interfaces}")
        if self.interface_id not in self.dgilib_extra.enabled_interfaces:
            self.dgilib_extra.interface_enable(self.interface_id)
            self.dgilib_extra.enabled_interfaces.append(self.interface_id)

    def disable(self):
        """disable

        Disable the interface.
        """
        if self.interface_id in self.dgilib_extra.enabled_interfaces:
            self.dgilib_extra.interface_disable(self.interface_id)
            self.dgilib_extra.enabled_interfaces.remove(self.interface_id)

    def read(self, *args, **kwargs):
        """read

        Read data from the interface.

        Returns
        -------
        InterfaceData

        """
        # Return the data
        return None

    def write(self, *args, **kwargs):
        """write

        Write data to the interface (currently unimplemented).

        """
        pass

    def init_csv_writer(self, log_folder=getcwd(), newline='', mode='w'):
        """
        init_csv_writer
        """
        # Open file handle
        self.file_handle = open(path.join(
            log_folder, (self.file_name_base + '_' + self.name + ".csv")),
            mode, newline=newline)
        # Create csv.writer
        self.csv_writer = csv.writer(self.file_handle)
        # Write header to file
        self.csv_writer.writerow(self.csv_header)

    def close_csv_writer(self):
        """
        close_csv_writer
        """
        # Close file handle
        self.file_handle.close()

    def csv_write_rows(self, interface_data):
        """
        csv_write_rows
        """
        self.csv_writer.writerows(interface_data)

    def csv_read_file(self, file_path=None, newline='', mode='r'):
        """
        csv_read_file
        """
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
