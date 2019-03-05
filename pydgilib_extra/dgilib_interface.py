"""This module provides a base interface class."""

from pydgilib_extra.dgilib_extra_exceptions import InterfaceNotAvailableError
from pydgilib_extra.dgilib_extra_config import INTERFACES


class DGILibInterface(object):
    """Provides a base interface class."""

    name = "interface_name"
    csv_header = ["timestamps", "values"]

    is_polling = False

    def __init__(self, dgilib_extra, interface_id, *args, **kwargs):
        """Instantiate DGILibInterfaceGPIO object."""
        self.file_handle = None
        self.csv_writer = None
        # Argument parsing
        self.dgilib_extra = dgilib_extra
        self.interface_id = interface_id
        self.verbose = kwargs.get("verbose", 0)
        # Set interface configuration
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
        :rtype: InterfaceData()
        """
        # Return the data
        return None

    def write(self, *args, **kwargs):
        """Read data from the interface."""
        pass

    def start(self):
        """Start polling."""
        if not self.is_polling:
            self.dgilib_extra.start_polling()

    def stop(self):
        """Stop polling."""
        if self.is_polling:
            self.dgilib_extra.stop_polling()

    def csv_write_rows(self, interdace_data):
        """csv_write_rows."""
        self.csv_writer.writerows(interdace_data)
