"""This module provides ___ ."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: dgilib_logger.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

#from pydgilib_extra.dgilib_extra_config import *

def mergeData(data1, data2):
    """Make class for data structure? Or at least make a method to merge that mutates the list instead of doing multiple copies
    """

    assert (data1.keys() == data2.keys())
    for interface_id in data1.keys():
        for col in range(len(data1[interface_id])):
            data1[interface_id][col].extend(data2[interface_id][col])
    return data1