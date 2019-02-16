"""This module provides Python bindings for DGILibExtra Logger."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: dgilib_logger.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

from time import sleep
import csv
from os import curdir, path, open, close

from pydgilib_extra.dgilib_extra_config import *


class DGILibLogger(object):
    """Python bindings for DGILib Logger.
    
        interfaces
            - GPIO mode
            - Power mode
    """

    def __init__(self, *args, **kwargs):
        """
        
        All kwargs will also be passed to 
        """
        
        # Get enabled loggers
        self.loggers = kwargs.get("loggers",[])
        
        # Enable the csv logger if file_name_base or log_folder has been specified.
        if LOGGER_CSV not in self.loggers and ("file_name_base" in kwargs or "log_folder" in kwargs):
            self.loggers.append(LOGGER_CSV)
            self.file_handles = {}
            self.csv_writers = {}
    
        # file_name_base - merely the optional base of the filename. Preferably leave standard
        # log_folder - where log files will be saved
        self.file_name_base = kwargs.get("file_name_base","log")
        self.log_folder = kwargs.get("log_folder",curdir)

        # Import matplotlib.pyplot as plt if LOGGER_PLOT in self.loggers and no figure has been specified
        if LOGGER_PLOT in self.loggers and "file_name_base" not in kwargs:
            import matplotlib.pyplot as plt
        
        # Enable the plot logger if figure has been specified.
        if LOGGER_PLOT not in self.loggers and ("figure" in kwargs):
            self.loggers.append(LOGGER_PLOT)
        
        # Set self.figure if LOGGER_PLOT enabled.
        if LOGGER_PLOT in self.loggers:
            self.figure = kwargs.get("figure",plt.figure())
            
        # Enable the object logger if data_in_obj exists and is True.
        if LOGGER_OBJECT not in self.loggers and kwargs.get("data_in_obj", False):
            self.loggers.append(LOGGER_OBJECT)
        
#         update_callback?
#         output = csv.writer(open('export_log.csv', 'w'))

        
    def __enter__(self):
        """
        """
        
        print(f"power_buffers at logger {self.power_buffers}")
        
#         if self.file_name is not None:
#             # TODO per interface
#             self.writer = "csv.writer"(open(file_name, 'w'))
        
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        """
        
        # Stop any running logging actions ??
        self.logger_stop()

    def logger_start(self):
        
        if LOGGER_CSV in self.loggers:
            for interface_id in self.enabled_interfaces:
                # Open file handle
                self.file_handle[interface_id] = open(path.join(self.log_folder, self.file_name_base + str(interface_id) + ".csv"), 'w') # TODO: Paths
                # Create csv.writer
                self.csv_writer[interface_id] = csv.writer(self.file_handle[interface_id])
            # Write header to file
            if INTERFACE_GPIO in self.enabled_interfaces:
                self.csv_writer[INTERFACE_GPIO].writerow(LOGGER_CSV_HEADER[INTERFACE_GPIO])
            if self.power_buffers:
                self.csv_writer[INTERFACE_POWER].writerow(LOGGER_CSV_HEADER[INTERFACE_POWER][self.power_buffers[0]["power_type"]]) # TODO: Clean this mess up, depending on how range mode and voltae mode work. If they dont work remove all stuff related to them.
        
        self.start_polling()
        self.auxiliary_power_start()
        
    def update_callback(self):
        
        # Get data
        data = {}
        if INTERFACE_GPIO in self.enabled_interfaces:
            data[INTERFACE_GPIO] = self.gpio_read()
        if self.power_buffers:
            data[INTERFACE_POWER] = self.power_read_buffer(self.power_buffers[0])
        
        # Write to registered loggers TODO
        if LOGGER_CSV in self.loggers:
            if INTERFACE_GPIO in self.enabled_interfaces:
                self.csv_writer[INTERFACE_GPIO].writerows(zip(*data[INTERFACE_GPIO]))
            if self.power_buffers:
                self.csv_writer[INTERFACE_POWER].writerows(zip(*data[INTERFACE_POWER]))
        
        # return the data
        return data
        
    def logger_stop(self):
        
        if LOGGER_CSV in self.loggers:
            for interface_id in self.enabled_interfaces:
                # Close csv.writer
#                 self.csv_writer[interface_id] = None
                # Close file handle
                close(self.file_handle[interface_id])
            
            
        self.stop_polling()
        self.auxiliary_power_stop()

    def logger(self, duration=10):
        """logger
        """
        
        

        self.logger_start()
        sleep(duration)
        data = self.update_callback()

        self.logger_stop()
        
        return data
