from time import sleep
import csv

from pydgilib_extra.dgilib_extra_config import *
from pydgilib_extra.dgilib_interface_gpio import gpio_augment_edges

import matplotlib.pyplot as plt; plt.ion()

from matplotlib.widgets import Slider, Button

class DGILibPlot(object):

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

        # We need the Line2D object as well, to update it
        if (len(self.ax.lines) == 0):
            self.ln, = self.ax.plot([], [], 'r-')
        else:
            self.ln = self.ax.lines[0]
            ln.set_xdata([])
            ln.set_ydata([])

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
        if "pins_correction_forward" not in kwargs:
            self.pins_correction_forward = 0.00075
        else:
            self.pins_correction_forward = kwargs.get("pins_correction_forward", True)

        if "pins_interval_shrink" not in kwargs:
            self.pins_interval_shrink = 0.0010
        else:
            self.pins_interval_shrink = kwargs.get("pins_interval_shrink", True)

        if "plot_interactivity_pause" not in kwargs:
            self.plot_interactivity_pause = 0.5
        else:
            self.plot_interactivity_pause = kwargs.get("plot_interactivity_pause", True)

        # Hardwiring these values to 0
        self.plot_xmin = 0
        self.plot_ymin = 0

        # We absolutely need these values from the user (or from the superior class), hence no default values
        # TODO: Are they really needed though?
        self.division = kwargs.get("division", True)
        self.duration = kwargs.get("duration", True)

        # We'll have some sliders to zoom in and out of the plot, as well as a cursor to move around when zoomed in
        # Leave space for sliders at the bottom
        plt.subplots_adjust(bottom=0.25)
        # Show grid
        plt.grid()

        # Slider color
        self.axcolor = 'lightgoldenrodyellow'
        # Title format
        # Should use this https://matplotlib.org/gallery/recipes/placing_text_boxes.html
        self.title_avg = "Total avg curr: %1"
        self.title_vis = "Visible avg curr: %1"
        self.title_pin = "Avg curr in %1: %2" # "calculate_average(data[INTERFACE_POWER])*1e3:.4} mA"
        self.title_time = "Time spent in %1: %2"
        self.ax.set_title("Waiting for data...")

        # Hold times for pins list, we're going to collect them
        self.hold_times = []
        self.hold_times_sum = 0.00

        self.colors = ["red","orange","blue","green"]

        self.initialize_sliders()

    def initialize_sliders(self):
        self.axpos = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=self.axcolor)
        self.axwidth = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=self.axcolor)
        self.resetax = plt.axes([0.8, 0.025, 0.1, 0.04])

        self.spos = Slider(self.axpos, 'x (s)', 0, min(0, self.duration-self.plot_xmax), valinit=0, valstep=0.5)
        self.swidth = Slider(self.axwidth, 'xmax', 0, self.duration, valinit=0, valstep=0.5)
        
        self.resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
        self.resetbtn = Button(self.resetax, 'Reset', color=self.axcolor, hovercolor='0.975')

        # I'm not sure how to detach these without them forgetting their parents (sliders)
        def update(val):
            pos = self.spos.val
            width = self.swidth.val

            if pos > (self.duration - width):
                pos = self.duration - width

            self.apos.clear()
            self.spos.__init__(apos, 'Position', 0, self.duration - width, valinit=pos, valstep=0.5)
            self.spos.on_changed(update)

            self.axes.axis([pos, pos+width, self.xmin, self.xmax])

            # TODO: Update
            #visible_average = calculate_average_midpoint_multiple_intervals(self.data, all_hold_times, i, i+width) * 1000
            #all_average = calculate_average_midpoint_multiple_intervals(self.data, all_hold_times, min(xdata), max(xdata)) * 1000

            #self.axes.set_title("Visible average: %.6f mA;\n Total average: %.6f mA." % (visible_average, all_average))

            fig.canvas.draw_idle()

        self.spos.on_changed(update)
        self.swidth.on_changed(update)

        def reset(event):
            self.swidth.reset()
            self.spos.__init__(self.apos, 'Position', 0, self.duration - self.xmax, valinit=0, valstep=0.5)
            self.spos.on_changed(update)
            self.spos.reset()

            # TODO: Update parameters
            #visible_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, i, i+width) * 1000
            #all_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, min(xdata), max(xdata)) * 1000

            #self.axes.set_title("Visible average: %.6f mA;\n Total average: %.6f mA." % (visible_average, all_average))
            
        self.resetbtn.on_clicked(reset)

    def update_plot(self, data):
        if not plt.fignum_exists(fig.number): 
            plt.show()
        else:
            plt.draw()
            plt.pause(self.plot_interactivity_pause)

        # I presume I already have this
        # for j in range(len(data[INTERFACE_POWER][0]))[1:]:
        #     xdata.append(i + data[INTERFACE_POWER][0][j])
        #     ydata.append(data[INTERFACE_POWER][1][j])

        # for pin_idx in range(len(self.plot_pins):

        #     if self.plot_pins[pin_idx] == True:
            
        #         for hold_times in identify_hold_times(data, self.plot_pins[pin_idx], pin_idx, correction_forward = self.pins_correction_forward, shrink = self.pins_interval_shrink):
            
        #             axes.axvspan(hold_times[0], hold_times[1], color=self.pins_colors[pin_idx], alpha=0.5)

        #             self.hold_times.append((hold_times[0], hold_times[1]))
        #             self.hold_times_sum += hold_times[1] - hold_times[0]

        self.ln.set_xdata(xdata)
        self.ln.set_ydata(ydata)

        # if spos.val == i - width:
        #     axes.axis([i,i+width,plot_min,plot_max])
        #     spos.set_val(i)

        # visible_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, i, i+width) * 1000
        # all_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, min(xdata), max(xdata)) * 1000
        plt.pause(PAUSE_DURATION)

def calculate_average_leftpoint_single_interval(power_data, start_time=None, end_time=None):
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