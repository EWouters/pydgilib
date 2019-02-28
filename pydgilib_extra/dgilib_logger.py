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
from pydgilib_extra.dgilib_interface_gpio import DGILibInterfaceGPIO, gpio_augment_edges
from pydgilib_extra.dgilib_interface_power import DGILibInterfacePower


class DGILibLogger(DGILibInterfaceGPIO, DGILibInterfacePower):
    """Python bindings for DGILib Logger.

    Interfaces:
        - GPIO mode
        - Power mode
    """

    def __init__(self, *args, **kwargs):
        """

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
        if LOGGER_PLOT not in self.loggers and ("fig" in kwargs or "ax" in kwargs):
            self.loggers.append(LOGGER_PLOT)

        # Set self.figure if LOGGER_PLOT enabled.
        if LOGGER_PLOT in self.loggers:
            # if "fig" in kwargs: # It seems the second argument of kwargs.get always gets called, so this check prevents an extra figure from being created
            self.fig = kwargs.get("fig")
            if self.fig is None:
                self.fig = plt.figure(figsize=(8, 6))
            # if "ax" in kwargs: # It seems the second argument of kwargs.get always gets called, so this check prevents an extra axis from being created
            self.ax = kwargs.get("ax")
            if self.ax is None:
                self.ax = self.fig.add_subplot(1, 1, 1)
            self.plot_pins = kwargs.get("plot_pins", True)

        # Enable the object logger if data_in_obj exists and is True.
        if LOGGER_OBJECT not in self.loggers and kwargs.get("data_in_obj", False):
            self.loggers.append(LOGGER_OBJECT)
        if LOGGER_OBJECT in self.loggers:
            self.data = {}

        # Initialize interfaces
        DGILibInterfaceGPIO.__init__(self, *args, **kwargs)
        DGILibInterfacePower.__init__(self, *args, **kwargs)

    def __enter__(self):
        """
        """

        DGILibInterfaceGPIO.__enter__(self)
        DGILibInterfacePower.__enter__(self)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        """

        # Should be removed and updated every time update_callback is called
        if LOGGER_PLOT in self.loggers:
            if self.augment_gpio:
                gpio_augment_edges(self.data[INTERFACE_GPIO], self.gpio_delay_time, self.gpio_switch_time, self.data[INTERFACE_POWER][0][-1])
            self.fig, self.ax = logger_plot_data(self.data, self.plot_pins, self.fig, self.ax)
            # logger_plot_data(self.data, [r or w for r, w in zip(self.read_mode, self.write_mode)], self.plot_pins)

        DGILibInterfaceGPIO.__exit__(self, exc_type, exc_value, traceback)
        DGILibInterfacePower.__exit__(self, exc_type, exc_value, traceback)

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
            for interface_id in self.enabled_interfaces:
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
            # Check if any data has arrived
            if data[INTERFACE_GPIO]:
                # Write to registered loggers
                if LOGGER_CSV in self.loggers:
                    # self.csv_writers[INTERFACE_GPIO].writerows(zip(*data[INTERFACE_GPIO]))
                    self.csv_writers[INTERFACE_GPIO].writerows(
                        [
                            (timestamps, *pin_values)
                            for timestamps, pin_values in zip(*data[INTERFACE_GPIO])
                        ]
                    )
                # Merge data into self.data if LOGGER_OBJECT is enabled
                if LOGGER_OBJECT in self.loggers:
                    for col in range(len(self.data[INTERFACE_GPIO])):
                        self.data[INTERFACE_GPIO][col].extend(data[INTERFACE_GPIO][col])
                # Update the plot if LOGGER_PLOT is enabled
                if LOGGER_PLOT in self.loggers:
                    pass
                    # print("TODO: Update plot")

        if INTERFACE_POWER in self.enabled_interfaces:
            data[INTERFACE_POWER] = self.power_read_buffer(self.power_buffers[0])
            # Check if any data has arrived
            if data[INTERFACE_POWER]:
                # Write to registered loggers
                if LOGGER_CSV in self.loggers:
                    self.csv_writers[INTERFACE_POWER].writerows(zip(*data[INTERFACE_POWER]))
                # Merge data into self.data if LOGGER_OBJECT is enabled
                if LOGGER_OBJECT in self.loggers:
                    for col in range(len(self.data[INTERFACE_POWER])):
                        self.data[INTERFACE_POWER][col].extend(data[INTERFACE_POWER][col])
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
    """Calculate average value of the power_data using the left Riemann sum."""

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


def calculate_average_by_pin(data, pin=0, start_time=None, end_time=None):
    """Calculate average value of the data while pin is high, using the left Riemann sum."""

    if start_time is None:
        start_time = data[INTERFACE_POWER][0][0]
    if end_time is None:
        end_time = data[INTERFACE_POWER][0][-1]

    last_time = start_time

    power_sum = 0
    time_sum = 0

    power_index = 0

    for timestamp, pin_values in zip(*data[INTERFACE_GPIO]):
        while (pin_values[pin] and power_index < len(data[INTERFACE_POWER][0]) and data[INTERFACE_POWER][0][power_index] <= timestamp):
            if (data[INTERFACE_POWER][0][power_index] >= start_time and data[INTERFACE_POWER][0][power_index] <= end_time):
                power_sum += data[INTERFACE_POWER][1][power_index] * (data[INTERFACE_POWER][0][power_index] - last_time)
                time_sum += (data[INTERFACE_POWER][0][power_index] - last_time)
            last_time = data[INTERFACE_POWER][0][power_index]
            power_index += 1

    if time_sum == 0:
        return 0
    return power_sum / time_sum


# Should be removed and updated every time update_callback is called
def logger_plot_data(data, plot_pins=[True]*4, fig=None, ax=None):
    if ax is None:
        if fig is None:
            fig = plt.figure(figsize=(8, 6))
        else:
            fig.clf()
        ax = fig.add_subplot(1, 1, 1)
    # plt.gcf().set_size_inches(8, 6, forward=True)
    ax.plot(*data[INTERFACE_POWER])
    if data[INTERFACE_POWER][1]:
        max_data = max(*data[INTERFACE_POWER][1])
    else:
        print("NO DATA ???")
        return
    for pin, plot_pin in enumerate(plot_pins):
        if plot_pin:
            ax.plot(data[INTERFACE_GPIO][0], [d[pin]*max_data for d in data[INTERFACE_GPIO][1]])
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Current [A]')
    # ax.set_title(f"Average current: {calculate_average(data[INTERFACE_POWER])*1e3:.4} mA, with pin 2 high: {calculate_average(power_filter_by_pin(2, data))*1e3:.4} mA, with pin 3 high: {calculate_average(power_filter_by_pin(3, data))*1e3:.4}")
    ax.set_title(f"Average current: {calculate_average(data[INTERFACE_POWER])*1e3:.4} mA, with pin 2 high: {calculate_average_by_pin(data, 2)*1e3:.4} mA, with pin 3 high: {calculate_average_by_pin(data, 3)*1e3:.4}")
    fig.suptitle("Logged Data")
    fig.show()
    
    return fig, ax

def power_and_time_per_pulse(data, pin, verbose=0, power_factor=1e3):
    """Calculate power and time per pulse.
    
    Takes the data and a pin and returns a list of power and time sums for each pulse of the specified pin.
    It stops when all pins are high.
    
    :param data: Data structure holding the samples.
    :type data: dict(256:list(list(float), list(float)), 48:list(list(float), list(list(bool))))
    :param pin: Number of the pin to be used.
    :type pin: int
    :return: List of list of power and time sums.
    :rtype: tuple(list(float), list(float))
    """
    pin_value = False

    charges = []
    times = []

    power_index = 0
    power_sum = 0
    time_sum = 0

    start_time = 0
    end_time = 0
    last_time = 0

    for timestamp, pin_values in zip(*data[INTERFACE_GPIO]):
        if all(pin_values):
            if verbose:
                print(f"power_and_time_per_pulse done, charges: {len(currents)}, times: {len(times)}")
            break
        if not pin_value and pin_values[pin]:
            pin_value = True
            start_time = timestamp
            last_time = timestamp
        if pin_value and not pin_values[pin]:
            pin_value = False
            end_time = timestamp
            while (power_index < len(data[INTERFACE_POWER][0]) and data[INTERFACE_POWER][0][power_index] <= end_time):
                if (data[INTERFACE_POWER][0][power_index] >= start_time):
                    power_sum += data[INTERFACE_POWER][1][power_index] * (data[INTERFACE_POWER][0][power_index] - last_time)
                    time_sum += (data[INTERFACE_POWER][0][power_index] - last_time)
                last_time = data[INTERFACE_POWER][0][power_index]
                power_index += 1

            charges.append(power_sum*power_factor)
            times.append(time_sum)
            power_sum = 0
            time_sum = 0
                
    return charges, times