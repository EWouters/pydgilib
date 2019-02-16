"""This module provides Python bindings for DGILibExtra Logger."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: dgilib_logger.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

from time import sleep
import csv


class DGILibLogger(object):
    """Python bindings for DGILib Logger.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        
        # Argument parsing
#         interfaces
#             - GPIO mode
#             - Power mode
        
#         file_name
#         plot
        
#         update_callback
        
        self.interfaces   = kwargs.get("interfaces",[])  # List of interfaces (ints)
#         self.interface_configs = {}
#         if INTERFACE_GPIO in self.interfaces:
#             self.interface_configs[INTERFACE_GPIO]   = kwargs.get("interface_configs",[])  # List of interfaces (ints)
        self.file_name    = kwargs.get("file_name",None)  # File name (passed to open), if empty no logging will be done.
        self.data_in_obj  = kwargs.get("data_in_obj",False)  # if this is true the data will be available through self.timestamp[INTERFACE] and self.data[INTERFACE]
        

#         output = csv.writer(open('export_log.csv', 'w'))

#         for foo in bar:
#            # do work
#            output.writerow([status, view, filename, out, err, current_time])
        
        
#         self.options = {
#             'option1' : 'default_value1',
#             'option2' : 'default_value2',
#             'option3' : 'default_value3', }

#         self.options.update(kwargs)
#         print self.options
        
    def __enter__(self):
        """
        """
        
        if self.file_name is not None:
            # TODO per interface
            self.writer = "csv.writer"(open(file_name, 'w'))
        
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        """
        
            

    def logger_start(self):
        self.start_polling()
        self.auxiliary_power_start()
        
    def logger_stop(self):
        self.stop_polling()
        self.auxiliary_power_stop()

    def logger(self, duration=10):
        """logger
        """
        
        
#         self.writer[INTERFACE_GPIO].writerow(['status', 'view', 'filename', 'stdout', 'stderr', 'time'])

        self.logger_start()
        sleep(duration)
        power_data = self.power_read()
        gpio_data = self.gpio_read()

        self.logger_stop()

        return power_data[0], gpio_data