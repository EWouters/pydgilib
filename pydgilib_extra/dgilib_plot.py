"""This module provides Python bindings for DGILibExtra Logger."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: dgilib_logger.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

from time import sleep
import csv

from pydgilib_extra.dgilib_extra_config import *
from pydgilib_extra.dgilib_interface_gpio import gpio_augment_edges

import matplotlib.pyplot as plt; plt.ion()

class DGILibLogger(object):

	def __init__(self, *args, **kwargs):

		# Maybe the user wants to put the power figure along with other figures he wants
		# if "fig" in kwargs: # It seems the second argument of kwargs.get always gets called, so this check prevents an extra figure from being created
        self.fig = kwargs.get("fig")
        if self.fig is None:
            self.fig = plt.figure(figsize=(8, 6))
        # if "ax" in kwargs: # It seems the second argument of kwargs.get always gets called, so this check prevents an extra axis from being created
        self.ax = kwargs.get("ax")
        if self.ax is None:
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Current (A)')

        # Initialize xmax, ymax of plot initially
        if "plot_xmax" not in kwargs:
            self.plot_xmax = -1 # Auto TODO: To be implemented
            self.ax.set_xlim(0, 5)
        else:
            self.plot_xmax = kwargs.get("plot_xmax", True)
            self.ax.set_xlim(0, self.plot_xmax)

        if "plot_ymax" not in kwargs:
            self.plot_ymax = -1 # Auto TODO: To be implemented
            self.ax.set_ylim(0, 0.035)
        else:
            self.plot_ymax = kwargs.get("plot_ymax", True)
            self.ax.set_ylim(0, self.plot_ymax)

        self.plot_pins = kwargs.get("plot_pins", True)

        # We need this since pin toggling is not aligned with power values changing when blinking a LED on the board, for example
        self.pins_correction_forward = kwargs.get("pins_correction_forward", True)
        self.pins_interval_shrink = kwargs.get("pins_interval_shrink", True)

        # We'll have some sliders to zoom in and out of the plot, as well as a cursor to move around when zoomed in
        # Leave space for sliders at the bottom
        plt.subplots_adjust(bottom=0.25)
        # Show grid
        plt.grid()

    


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