"""This module provides Python bindings for DGILibExtra Logger."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: dgilib_logger.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

from time import sleep
import csv
from os import curdir, path
import copy

# Todo, remove dependency
import matplotlib.pyplot as plt

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
        self.loggers = kwargs.get("loggers", [])

        # Enable the csv logger if file_name_base or log_folder has been specified.
        if LOGGER_CSV not in self.loggers and (
            "file_name_base" in kwargs or "log_folder" in kwargs
        ):
            self.loggers.append(LOGGER_CSV)
        if LOGGER_CSV in self.loggers:
            self.file_handles = {}
            self.csv_writers = {}

        # file_name_base - merely the optional base of the filename. Preferably leave standard
        # log_folder - where log files will be saved
        self.file_name_base = kwargs.get("file_name_base", "log")
        self.log_folder = kwargs.get("log_folder", curdir)

        # Import matplotlib.pyplot as plt if LOGGER_PLOT in self.loggers and no figure has been specified
        if LOGGER_PLOT in self.loggers:
            import matplotlib.pyplot as plt

        # Enable the plot logger if figure has been specified.
        if LOGGER_PLOT not in self.loggers and ("figure" in kwargs):
            self.loggers.append(LOGGER_PLOT)

        # Set self.figure if LOGGER_PLOT enabled.
        if LOGGER_PLOT in self.loggers:
            self.figure = kwargs.get("figure", plt.figure(figsize=(8, 6)))

        # Enable the object logger if data_in_obj exists and is True.
        if LOGGER_OBJECT not in self.loggers and kwargs.get("data_in_obj", False):
            self.loggers.append(LOGGER_OBJECT)
        if LOGGER_OBJECT in self.loggers:
            self.data = {}

#         update_callback?
#         output = csv.writer(open('export_log.csv', 'w'))

    def __enter__(self):
        """
        """

#         print(f"power_buffers at logger {self.power_buffers}")

#         if self.file_name is not None:
#             # TODO per interface
#             self.writer = "csv.writer"(open(file_name, 'w'))

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        """

        # Should be removed and updated every time update_callback is called
        if LOGGER_PLOT in self.loggers:
            logger_plot_data(self.data)

        # Stop any running logging actions ??
#         self.logger_stop()

    def logger_start(self):

        if LOGGER_CSV in self.loggers:
            for interface_id in self.enabled_interfaces:
                # Open file handle
                self.file_handles[interface_id] = open(
                    path.join(
                        self.log_folder,
                        self.file_name_base + str(interface_id) + ".csv",
                    ),
                    "w",
                )
                # Create csv.writer
                self.csv_writers[interface_id] = csv.writer(
                    self.file_handles[interface_id]
                )
            if self.power_buffers:
                # Open file handle
                self.file_handles[INTERFACE_POWER] = open(
                    path.join(
                        self.log_folder,
                        self.file_name_base + str(INTERFACE_POWER) + ".csv",
                    ),
                    "w",
                )
                # Create csv.writer
                self.csv_writers[INTERFACE_POWER] = csv.writer(
                    self.file_handles[INTERFACE_POWER]
                )

            # Write header to file
            for interface_id in self.enabled_interfaces:
                self.csv_writers[interface_id].writerow(
                    LOGGER_CSV_HEADER[interface_id]
                )
            if self.power_buffers:
                self.csv_writers[INTERFACE_POWER].writerow(
                    LOGGER_CSV_HEADER[INTERFACE_POWER][
                        self.power_buffers[0]["power_type"]
                    ]
                ) # TODO: Clean this mess up, depending on how range mode and voltage mode work. If they dont work remove all stuff related to them.

        # Create data structure self.data if LOGGER_OBJECT is enabled
        if LOGGER_OBJECT in self.loggers:
            for interface_id in self.enabled_interfaces + [INTERFACE_POWER] * bool(self.power_buffers):
                self.data[interface_id] = [[], []]

        # Create axes self.axes if LOGGER_PLOT is enabled
        if LOGGER_PLOT in self.loggers:
            pass
            # print("TODO: Create axes, or what if they were parsed?")
                
        self.start_polling()
        self.auxiliary_power_start()

    def update_callback(self):

        # Get data
        data = {}
        if INTERFACE_GPIO in self.enabled_interfaces:
            data[INTERFACE_GPIO] = self.gpio_read()
        if self.power_buffers:
            data[INTERFACE_POWER] = self.power_read_buffer(self.power_buffers[0])

        # Write to registered loggers TODO PLOT
        if LOGGER_CSV in self.loggers:
            if INTERFACE_GPIO in self.enabled_interfaces:
                # self.csv_writers[INTERFACE_GPIO].writerows(zip(*data[INTERFACE_GPIO]))
                self.csv_writers[INTERFACE_GPIO].writerows(
                    [
                        (timestamps, *pin_values)
                        for timestamps, pin_values in zip(*data[INTERFACE_GPIO])
                    ]
                )
            if self.power_buffers:
                self.csv_writers[INTERFACE_POWER].writerows(zip(*data[INTERFACE_POWER]))

        # Merge data into self.data if LOGGER_OBJECT is enabled
        if LOGGER_OBJECT in self.loggers:
            self.data_add(data)

        # Update the plot if LOGGER_PLOT is enabled
        if LOGGER_PLOT in self.loggers:
            pass
            # print("TODO: Update plot")
        
        # return the data
        return data

    def logger_stop(self):

        self.stop_polling()
        self.auxiliary_power_stop()
        
        # Get last data from buffer
        data = self.update_callback()
        
        if LOGGER_CSV in self.loggers:
            for interface_id in self.enabled_interfaces:
                # Close file handle
                self.file_handles[interface_id].close()
            if self.power_buffers:
                # Close file handle
                self.file_handles[INTERFACE_POWER].close()

        return data

    def logger(self, duration=10):
        """logger
        
        TODO: call update_callback at specified intervals to avoid buffer overflows (figure out the formula based on the samplerate and buffersize)
        
        """

        self.logger_start()
        sleep(duration)
        # data = self.update_callback()
        # data = mergeData(data, self.update_callback())
        # data = mergeData(data, self.logger_stop())

        return self.logger_stop()

    def data_add(self, data):
        """
        """

        assert(self.data.keys() == data.keys())  # TODO create error
        for interface_id in data.keys():
            for col in range(len(self.data[interface_id])):
                self.data[interface_id][col].extend(data[interface_id][col])

    def power_filter_by_pin(self, pin=0, data=None):
        """

        Filters the data to when a specified pin is high
        """

        if data is None:
            data = self.data
        
        return power_filter_by_pin(pin, data, self.verbose)

    def calculate_average(self, power_data=None, start_time=None, end_time=None):
        """Calculate average value of the power_data using the left Riemann sum"""

        if power_data is None:
            power_data = self.data[INTERFACE_POWER]

        return calculate_average(power_data, start_time, end_time)

    # def pin_duty_cycle(self, pin=0, data=None):
    #     pass
    
def mergeData(data1, data2):
    """Make class for data structure? Or at least make a method to merge that mutates the list instead of doing multiple copies
    """
    
    assert(data1.keys() == data2.keys())
    for interface_id in data1.keys():
        for col in range(len(data1[interface_id])):
            data1[interface_id][col].extend(data2[interface_id][col])
    return data1


def power_filter_by_pin(pin, data, verbose=0):
    """

    Filters the data to when a specified pin is high
    """

    power_data = copy.deepcopy(data[INTERFACE_POWER])

    pin_value = False

    power_index = 0

    if verbose:
        print(f"power_filter_by_pin filtering  {len(power_data[0])} power samples.")
    
    for timestamp, pin_values in zip(*data[INTERFACE_GPIO]):
        while (power_index < len(power_data[0]) and power_data[0][power_index] < timestamp):
            power_data[1][power_index] *= pin_value
            power_index += 1

        if pin_values[pin] != pin_value:
            if verbose:
                print(f"\tpin {pin} changed at {timestamp}, {pin_value}")
            pin_value = pin_values[pin]

    return power_data

def calculate_average(power_data, start_time=None, end_time=None):
    """Calculate average value of the power_data using the left Riemann sum"""

    if start_time is None:
        start_time = power_data[0][0]

    if end_time is None:
        end_time = power_data[0][-1]

    last_time = start_time

    sum = 0

    for timestamp, power_value in zip(*power_data):
        sum += power_value * (timestamp - last_time)
        last_time = timestamp

    return sum / (end_time - start_time)

# Should be removed and updated every time update_callback is called
def logger_plot_data(data):
    # plt.gcf().set_size_inches(8, 6, forward=True)
    plt.plot(*data[INTERFACE_POWER])
    max_data = max(data[INTERFACE_POWER][1])
    for pin in range(4):
        plt.plot(data[INTERFACE_GPIO][0], [d[pin]*max_data for d in data[INTERFACE_GPIO][1]])
    plt.xlabel('Time')
    plt.ylabel('Current')
    plt.suptitle("Logged Data")
    plt.title(f"Average current: {calculate_average(data[INTERFACE_POWER])*1e3:.4} mA, with pin 2 high: {calculate_average(power_filter_by_pin(2, data))*1e3:.4} mA, with pin 3 high: {calculate_average(power_filter_by_pin(3, data))*1e3:.4}")
    plt.show()