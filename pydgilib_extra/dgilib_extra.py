"""This module provides user friendly way to interact with the DGILib API."""

from time import sleep

from pydgilib.dgilib import DGILib

from pydgilib.dgilib_config import INTERFACE_TIMESTAMP
from pydgilib_extra.dgilib_logger import DGILibLogger


class DGILibExtra(DGILib):
    """A user friendly way to interact with the DGILib API."""

    def __init__(self, *args, **kwargs):
        """Instantiate DGILibExtra object."""
        DGILib.__init__(self, *args, **kwargs)
        self.logger = DGILibLogger(self, *args, **kwargs)

        self.available_interfaces = []
        self.enabled_interfaces = []
        self.timer_factor = None

    def __enter__(self):
        """For usage in `with DGILibExtra() as dgilib:` syntax."""
        DGILib.__enter__(self)

        self.available_interfaces = self.interface_communication.interface_list()

        self.logger.__enter__()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """For usage in `with DGILibExtra() as dgilib:` syntax."""
        DGILibLogger.__exit__(self, exc_type, exc_value, traceback)

        for interface in self.enabled_interfaces:
            self.interface_communication.interface_disable(interface)

        self.logger.__exit__(exc_type, exc_value, traceback)

        if self.verbose:
            print("bye from DGILib Extra")

    def info(self):
        """Get the build information of DGILib.

        :return:  Version information of DGILib:
            - major_version: the major_version of DGILib
            - minor_version: the minor_version of DGILib
            - build_number: the build number of DGILib. 0 if not supported
            - major_fw: the major firmware version of the connected DGI device
            - minor_fw: the minor firmware version of the connected DGI device
        :rtype: tuple
        """
        major_version = self.get_major_version()
        minor_version = self.get_minor_version()
        build_number = self.get_build_number()
        major_fw, minor_fw = self.get_fw_version()

        return major_version, minor_version, build_number, major_fw, minor_fw

    def device_reset(self, duration=1):
        """Set the device reset line for duration seconds."""
        self.target_reset(True)
        sleep(duration)
        self.target_reset(False)

    def get_time_factor(self):
        """Get the factor to multiply timestamps by to get seconds.

        :return: timer_factor
        :rtype: double
        """
        _, config_value = self.interface_get_configuration(INTERFACE_TIMESTAMP)
        timer_prescaler = config_value[0]
        timer_frequency = config_value[1]

        if self.verbose:
            print(
                f"timer_factor: {timer_prescaler / timer_frequency}, "
                f"timer_prescaler: {timer_prescaler}, timer_frequency: "
                f"{timer_frequency}")

        return timer_prescaler / timer_frequency
