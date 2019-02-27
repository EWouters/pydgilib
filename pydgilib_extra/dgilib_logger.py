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

from pydgilib_extra.dgilib_extra_config import *
from pydgilib_extra.dgilib_interface_gpio import gpio_augment_edges
from pydgilib_extra.dgilib_plot import *

import matplotlib.pyplot as plt; plt.ion()

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
            
        # Plot wants to use self.data later and there's no self.data without LOGGER_OBJECT
        if LOGGER_OBJECT not in self.loggers and (LOGGER_PLOT in self.loggers):
            self.loggers.append(LOGGER_OBJECT)

        # Enable the plot logger if figure has been specified.
        if LOGGER_PLOT not in self.loggers and ("fig" in kwargs or "ax" in kwargs):
            self.loggers.append(LOGGER_PLOT)

        # Enable the object logger if data_in_obj exists and is True.
        if LOGGER_OBJECT not in self.loggers and kwargs.get("data_in_obj", False):
            self.loggers.append(LOGGER_OBJECT)
        if LOGGER_OBJECT in self.loggers:
            self.data = {}

        # Import matplotlib.pyplot as plt if LOGGER_PLOT in self.loggers and no figure has been specified
        if LOGGER_PLOT in self.loggers:
            # import matplotlib.pyplot as plt
            # Matplotlib interactivity on: So the plot itself does not freeze the terminal and program until it gets quit
            # plt.ion() 

            self.plotobj = DGILibPlot(**kwargs)

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
            #gpio_augment_edges(self.data[INTERFACE_GPIO])
            self.fig = logger_plot_data(self.data, self.plot_pins, self.fig, self.ax)
            # logger_plot_data(self.data, [r or w for r, w in zip(self.read_mode, self.write_mode)], self.plot_pins)

        # Stop any running logging actions ??
        self.logger_stop()

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
            logger_plot_data(self.data, plot_pins="hold", fig=self.fig, ax=self.ax)
            # print("TODO: Create axes, or what if they were parsed?")
        
        self.start_polling()
        self.auxiliary_power_start()

    def update_callback(self, iteration = 0):
        # Get data
        data = {}
        if INTERFACE_GPIO in self.enabled_interfaces:
            data[INTERFACE_GPIO] = self.gpio_read()
        if self.power_buffers:
            data[INTERFACE_POWER] = self.power_read_buffer(self.power_buffers[0])

        if data[INTERFACE_GPIO] or data[INTERFACE_POWER]:
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
            # if LOGGER_OBJECT in self.loggers:
            #     self.data_add(shift_data(data, iteration))

            # Update the plot if LOGGER_PLOT is enabled
            if LOGGER_PLOT in self.loggers:
                logger_plot_data(self.data, plot_pins="hold", fig=self.fig, ax=self.ax)
                # print("TODO: Update plot")
        elif self.verbose:
            print("update_callback: No new data")
        
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

    def logger(self, duration=60, division = 10):
        """logger
        
        TODO: call update_callback at specified intervals to avoid buffer overflows (figure out the formula based on the samplerate and buffersize)
              ... put the calculated value based on formula as default initial value for 'division' parameter
        """

        self.logger_start()

        # What if division < duration?
        pause_with = min(division, duration)

        iteration = 0.0
        while iteration < duration:
            plt.pause(pause_with)
            self.data = merge_data(self.data, shift_data(self.update_callback(), iteration))
            iteration += pause_with
        #self.data = merge_data(self.data, self.logger_stop())

        print("Stopping")
        self.logger_stop()

        return self.data

    # This is the same as merge_data

    # def data_add(self, data):
    #     """
    #     """

    #     assert(self.data.keys() == data.keys())  # TODO create error
    #     for interface_id in data.keys():
    #         for col in range(len(self.data[interface_id])):
    #             self.data[interface_id][col].extend(data[interface_id][col])

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
    

def merge_data(data1, data2):
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

global_ln = None

# Should be removed and updated every time update_callback is called
def logger_plot_data(data, plot_pins="hold", fig=None, ax=None, listen_to = [False,False,True,False], listen_for = [False,False,False,False], pins_correction_forward=0.00, pins_interval_shrink=0.00):
    global global_ln

    if ax is None:
        if fig is None:
            fig = plt.figure(figsize=(8, 6))
        else:
            fig.clf()
        ax = fig.add_subplot(1, 1, 1)
    # plt.gcf().set_size_inches(8, 6, forward=True)

    ln = None
    if (len(ax.lines) == 0):
        ln, = ax.plot(*data[INTERFACE_POWER], 'r-')
        global_ln = ln
    else:
        ln = ax.lines[0]
        ln.set_xdata(data[INTERFACE_POWER][0])
        ln.set_ydata(data[INTERFACE_POWER][1])

    if data[INTERFACE_POWER][1]:
        max_data = max(*data[INTERFACE_POWER][1])
    else:
        ax.set_title("Waiting for data...")
        return

    # Plotting the pins as 
    if plot_pins == "hold":
        colors = ["black", "brown", "blue", "green"]
        for pin in range(4):
            if not listen_for[pin]: continue

            for hold_times in identify_hold_times(data, listen_to[pin], pin, correction_forward = pins_correction_forward, shrink = pins_interval_shrink):
                axes.axvspan(i+hold_times[0], i+hold_times[1], color=colors[pin], alpha=0.5)

                all_hold_times.append((i+hold_times[0], i+hold_times[1]))
                all_hold_times_sum += hold_times[1] - hold_times[0]

    ax.set_title(f"Average current: {calculate_average(data[INTERFACE_POWER])*1e3:.4} mA, \nwith pin 2 high: {calculate_average(power_filter_by_pin(2, data))*1e3:.4} mA,\n with pin 3 high: {calculate_average(power_filter_by_pin(3, data))*1e3:.4} mA")
    #fig.suptitle("Logged Data")

    if not plt.fignum_exists(fig.number):
        plt.show()
    else:
        plt.draw()
        plt.pause(0.5)
    
    # return fig, ax

def identify_hold_times(whole_data, true_false, pin, correction_forward = 0.00, shrink = 0.00):
    data = whole_data[INTERFACE_GPIO]
    hold_times = []
    start = data[0][0]
    end = data[0][0]
    in_hold = true_false
    not_in_hold = not true_false
    search = not true_false

    interval_sizes = []

    for i in range(len(data[0])):
        if search == not_in_hold: # Searching for start of hold time 
            if data[1][i][pin] == search:
                start = data[0][i]
            else:
                end = data[0][i]
                search = not search

        if search == in_hold: # Searching for end of hold time
            if data[1][i][pin] == search:
                end = data[0][i]
            else:
                search = not search
                to_add = (start+correction_forward+shrink,end+correction_forward-shrink)
                if ((to_add[0] != to_add[1]) and (to_add[0] < to_add[1])):
                    hold_times.append(to_add)
                    interval_sizes.append(to_add[1] - to_add[0])
                start = data[0][i]

    should_add_last_interval = True
    for ht in hold_times:
        if (ht[0] == start): should_add_last_interval = False

    if should_add_last_interval:

        invented_end_time = whole_data[INTERFACE_POWER][0][-1]+correction_forward-shrink

        # This function ASSUMES that the intervals are about the same in size.
        # ... If the last interval that should be highlighted on the graph is
        # ... abnormally higher than the maximum of the ones that already happened 
        # ... correctly then cancel highlighting with the help of 'invented_end_time' 
        # ... and highlight using the minimum from the 'interval_sizes' list, to get
        # ... an average that is most likely unaffected by stuff happening at the end
        # ... of the interval, which the power interface from the board failed to
        # ... communicate to us.
        if ((invented_end_time - start) > max(interval_sizes)):
            invented_end_time = start + min(interval_sizes)

        to_add = (start+correction_forward+shrink,invented_end_time)

        if ((to_add[0] != to_add[1]) and (to_add[0] < to_add[1])):
            hold_times.append(to_add)

    return hold_times

def calculate_average_midpoint_single_interval(power_data, start_time = None, end_time = None):
    # Calculate average value using midpoint Riemann sum
    sum = 0
 
    actual_start_time = -1
    actual_end_time = -1
 
    for i in range(len(power_data[0]) - 1)[1:]:
        first_current_value = power_data[1][i]
        second_current_value = power_data[1][i+1]
        timestamp = power_data[0][i+1]
        last_time = power_data[0][i]
 
        if ((last_time >= start_time) and (last_time < end_time)):
            sum += ((first_current_value + second_current_value)/2) * (timestamp - last_time)
 
            # We have to select the actual start time and the actual 
            if (actual_start_time == -1): actual_start_time = power_data[0][i]
 
        if (timestamp >= end_time):
            actual_end_time = power_data[0][i-1]
            break
 
    return sum / (actual_end_time - actual_start_time)   

def calculate_average_midpoint_multiple_intervals(power_data, intervals, start_time = None, end_time = None):
    # Calculate average value using midpoint Riemann sum
    sum = 0
    to_divide = 0

    for intv in intervals:
        if ((intv[0] >= start_time) and (intv[0] <= end_time) and (intv[1] >= start_time) and (intv[1] <= end_time)):
            sum += calculate_average_midpoint_single_interval(power_data, intv[0], intv[1])
            to_divide += 1

    return sum / to_divide

def shift_data(data, shift_by):
    new_data = copy.deepcopy(data)

    for i in range(len(data[INTERFACE_POWER][0])):
        new_data[INTERFACE_POWER][0][i] = shift_by + data[INTERFACE_POWER][0][i]

    for i in range(len(data[INTERFACE_GPIO][0])):
        new_data[INTERFACE_GPIO][0][i] = shift_by + data[INTERFACE_GPIO][0][i]

    return new_data
