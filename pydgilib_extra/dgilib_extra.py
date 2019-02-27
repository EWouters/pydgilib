"""This module provides Python bindings for DGILib Extra."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: dgilib_extra.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

from time import sleep

from pydgilib.dgilib import DGILib

from pydgilib_extra.dgilib_extra_config import *
from pydgilib_extra.dgilib_interface_gpio import DGILibInterfaceGPIO
from pydgilib_extra.dgilib_interface_power import DGILibInterfacePower
from pydgilib_extra.dgilib_logger import DGILibLogger


class DGILibExtra(DGILib, DGILibInterfaceGPIO, DGILibInterfacePower, DGILibLogger):
    """Python bindings for DGILib Extra.
    """

    def __init__(self, *args, **kwargs):
        """
        """

        DGILib.__init__(self, *args, **kwargs)
        
        DGILibInterfaceGPIO.__init__(self, *args, **kwargs)
        DGILibInterfacePower.__init__(self, *args, **kwargs)
        DGILibLogger.__init__(self, *args, **kwargs)

        self.available_interfaces = []
        self.enabled_interfaces = []
        self.timer_factor = None

    def __enter__(self):
        """
        """

        DGILib.__enter__(self)

        self.available_interfaces = self.interface_list()
        
        DGILibInterfaceGPIO.__enter__(self)
        DGILibInterfacePower.__enter__(self)

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        DGILibLogger.__exit__(self, exc_type, exc_value, traceback)
        DGILibInterfaceGPIO.__exit__(self, exc_type, exc_value, traceback)
        # DGILibInterfacePower.__exit__(self, exc_type, exc_value, traceback)

        for interface in self.enabled_interfaces:
            self.interface_disable(interface)

        DGILib.__exit__(self, exc_type, exc_value, traceback)

        if self.verbose:
            print("bye from DGILib Extra")

    def info(self):
        """Get the build information of DGILib.
        
        :param print_info: A flag used to print the build information to the console (default is False)
        :type print_info: bool
        :return:  Version information of DGILib:
            - major_version: the major_version of DGILib
            - minor_version: the minor_version of DGILib
            - build_number: the build number of DGILib. 0 if not supported
            - major_fw: the major firmware version of the DGI device connected
            - minor_fw: the minor firmware version of the DGI device connected
        :rtype: tuple
        """

        major_version = self.get_major_version()
        minor_version = self.get_minor_version()
        build_number = self.get_build_number()
        major_fw, minor_fw = self.get_fw_version()

        return major_version, minor_version, build_number, major_fw, minor_fw

    def device_reset(self, duration=1):
        """Set the device reset line for duration seconds.
        """

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
                f"timer_factor: {timer_prescaler / timer_frequency}, timer_prescaler: {timer_prescaler}, timer_frequency: {timer_frequency}"
            )

        return timer_prescaler / timer_frequency