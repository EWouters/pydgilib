"""This module provides Python bindings for DGILib Extra."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: __init__.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

from pydgilib.dgilib import DGILib

from pydgilib_extra.dgilib_extra_config import *
from pydgilib_extra.dgilib_extra_exceptions import *
from pydgilib_extra.dgilib_extra import DGILibExtra
from pydgilib_extra.dgilib_logger import calculate_average, power_filter_by_pin, logger_plot_data, calculate_average_by_pin, power_and_time_per_pulse, mergeData
from pydgilib_extra.dgilib_interface_gpio import gpio_augment_edges