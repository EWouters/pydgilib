"""This module provides Python bindings for DGILib Extra."""

from pydgilib.dgilib import DGILib

from pydgilib.dgilib_config import *
from pydgilib_extra.dgilib_extra_config import *
# from pydgilib.dgilib_exceptions import *
# from pydgilib_extra.dgilib_extra_exceptions import *
from pydgilib_extra.dgilib_extra import DGILibExtra
from pydgilib_extra.dgilib_logger import DGILibLogger
from pydgilib_extra.dgilib_interface_gpio import DGILibInterfaceGPIO
from pydgilib_extra.dgilib_interface_power import DGILibInterfacePower
from pydgilib_extra.dgilib_data import (
    LoggerData, InterfaceData, valid_interface_data)
from pydgilib_extra.dgilib_calculations import *
from pydgilib_extra.dgilib_plot import DGILibPlot

__author__ = "EWouters <ehwo(at)kth.se>"
__url__ = "https://github.com/EWouters/Atmel-SAML11/tree/master/Python/" \
    "pydgilib"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/" \
    "2016"
__license__ = "BSD-3-Clause"
__version__ = "0.2"
__docformat__ = "reStructuredText"
