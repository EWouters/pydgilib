"""This module provides user friendly way to interact with the DGILib API."""

from time import sleep

from pydgilib.dgilib import DGILib

from pydgilib.dgilib_config import (
    INTERFACE_GPIO, INTERFACE_TIMESTAMP, INTERFACE_POWER_DATA)
from pydgilib_extra.dgilib_extra_config import (INTERFACES, INTERFACE_POWER)
from pydgilib_extra.dgilib_logger import DGILibLogger
from pydgilib_extra.dgilib_interface import DGILibInterface
from pydgilib_extra.dgilib_interface_gpio import DGILibInterfaceGPIO
from pydgilib_extra.dgilib_interface_power import DGILibInterfacePower


class DGILibExtra(DGILib):
    """A user friendly way to interact with the DGILib API."""

    def __init__(self, *args, **kwargs):
        """Instantiate DGILibExtra object."""

        # Set default values for attributes
        self.available_interfaces = []
        self.enabled_interfaces = []
        self.timer_factor = None
        self.interfaces = {}
        self.data = None
        # Instantiate base class
        DGILib.__init__(self, *args, **kwargs)
        # Store arguments
        self.args = args
        self.kwargs = kwargs

        if self.verbose >= 2:
            print("args: ", args)
            print("kwargs: ", kwargs)

    def __enter__(self):
        """For usage in `with DGILibExtra() as dgilib:` syntax."""
        DGILib.__enter__(self)
        self.available_interfaces = self.interface_list()
        if INTERFACE_POWER_DATA in self.available_interfaces:
            self.available_interfaces.append(INTERFACE_POWER)

        # Instantiate interface objects and enable the interfaces
        if "interfaces" in self.kwargs:
            for interface_id in self.kwargs["interfaces"]:
                self.interfaces[interface_id] = instantiate_interface(
                    interface_id, self)
                self.interfaces[interface_id].enable()

        # Instantiate logger if there were any loggers specified
        if self.kwargs.get("loggers", []):
            self.logger = DGILibLogger(
                self, *self.args, **self.kwargs)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """For usage in `with DGILibExtra() as dgilib:` syntax."""
        for interface in self.interfaces.values():
            interface.disable()

        DGILib.__exit__(self, exc_type, exc_value, traceback)

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

    def keep_plot(self):
        if self.plotobj is not None:
            self.plotobj.keep_plot()

    def plot_still_exists(self):
        if self.plotobj is not None:
            return self.plotobj.plot_still_exists()

    def hold_plot(self):
        if self.plotobj is not None:
            while self.plot_still_exists():
                self.keep_plot()
