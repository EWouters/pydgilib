from time import sleep
import csv

from pydgilib_extra.dgilib_extra_config import *
from pydgilib_extra.dgilib_interface_gpio import gpio_augment_edges
from pydgilib_extra.dgilib_logger_functions import mergeData

import matplotlib.pyplot as plt; plt.ion()
from matplotlib.widgets import Slider, Button

class DGILibPlot(object):

    def __init__(self, dgilib_extra, *args, **kwargs):
        self.dgilib_extra = dgilib_extra

        # Maybe the user wants to put the power figure along with other figures he wants
        # if "fig" in kwargs: # It seems the second argument of kwargs.get
            # always gets called, so this check prevents an extra figure from
            # being created
        self.fig = kwargs.get("fig")
        if self.fig is None:
            self.fig = plt.figure(figsize=(8, 6))
        # if "ax" in kwargs: # It seems the second argument of kwargs.get
            # always gets called, so this check prevents an extra axis from
            # being created
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
            self.ln.set_xdata([])
            self.ln.set_ydata([])

        # Initialize xmax, ymax of plot initially
        self.plot_xmax = kwargs.get("plot_xmax", None)
        if self.plot_xmax is None:
            self.plot_xauto = True
            self.plot_xmax = 10
        else:
            self.plot_xauto = False

        self.plot_ymax = kwargs.get("plot_ymax", None)
        if self.plot_ymax is None:
            self.plot_yauto = True
            self.plot_ymax = 0.0035
        else:
            self.plot_yauto = False

        self.plot_pins = kwargs.get("plot_pins", None)
        self.plot_pins_values = kwargs.get("plot_pins_values", None)
        self.plot_pins_method =  kwargs.get("plot_pins_method", "highlight")
        self.plot_pins_colors =  kwargs.get("plot_pins_colors", ["red", "orange", "blue", "green"])
        self.average_function =  kwargs.get("average_function", "leftpoint")

        # We need this since pin toggling is not aligned with power values changing when blinking a LED on the board, for example
        self.pins_correction_forward = kwargs.get("pins_correction_forward", 0.00075)
        self.pins_interval_shrink = kwargs.get("pins_interval_shrink", 0.0010)
        self.plot_pause_secs = kwargs.get("plot_interactivity_pause", 0.00000001)

        # Hardwiring these values to 0
        self.plot_xmin = 0
        self.plot_ymin = 0

        # We absolutely need these values from the user (or from the superior class), hence no default values
        # TODO: Are they really needed though?
        self.plot_xdiv = kwargs.get("plot_xdiv", min(5, self.plot_xmax))
        # self.duration = kwargs.get("duration", max(self.plot_xmax, 5))

        # We'll have some sliders to zoom in and out of the plot, as well as a cursor to move around when zoomed in
        # Leave space for sliders at the bottom
        plt.subplots_adjust(bottom=0.3)
        # Show grid
        plt.grid()

        # Slider color
        self.axcolor = 'lightgoldenrodyellow'
        # Title format
        # Should use this https://matplotlib.org/gallery/recipes/placing_text_boxes.html
        self.title_avg = "Total avg curr: %1"
        self.title_vis = "Visible avg curr: %1"
        self.title_pin = "Avg curr in %1: %2"  # "calculate_average(data[INTERFACE_POWER])*1e3:.4} mA"
        self.title_time = "Time spent in %1: %2"
        self.ax.set_title("Waiting for data...")

        # Hold times for pins list, we're going to collect them
        self.hold_times = []
        self.hold_times_sum = 0.00

        #self.data = {INTERFACE_GPIO: [[],[]], INTERFACE_POWER: [[],[]]}

        self.verbose = kwargs.get("verbose", 0)

        self.initialize_sliders()

    def initialize_sliders(self):
        self.axpos = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=self.axcolor)
        self.axwidth = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=self.axcolor)
        self.resetax = plt.axes([0.8, 0.025, 0.1, 0.04])

        self.spos = Slider(self.axpos, 'x', 0, self.plot_xmax - self.plot_xdiv, valinit=0, valstep=0.5)
        self.swidth = Slider(self.axwidth, 'xmax', 0, self.plot_xmax, valinit=self.plot_xdiv, valstep=0.5)
        self.resetbtn = Button(self.resetax, 'Reset', color=self.axcolor, hovercolor='0.975')

        self.xleftax = plt.axes([0.4, 0.025, 0.095, 0.04])  # x_pos, y_pos, width, height
        self.xrightax = plt.axes([0.5, 0.025, 0.095, 0.04])
        self.xmaxleftax = plt.axes([0.6, 0.025, 0.095, 0.04])
        self.xmaxrightax = plt.axes([0.7, 0.025, 0.095, 0.04])
        self.xleftbtn = Button(self.xleftax, '<x', color=self.axcolor, hovercolor='0.975')
        self.xrightbtn = Button(self.xrightax, 'x>', color=self.axcolor, hovercolor='0.975')
        self.xmaxleftbtn = Button(self.xmaxleftax, 'xmax-', color=self.axcolor, hovercolor='0.975')
        self.xmaxrightbtn = Button(self.xmaxrightax, 'xmax+', color=self.axcolor, hovercolor='0.975')
        self.xupbtn = Button(self.resetax, 'Reset', color=self.axcolor, hovercolor='0.975')
        self.xdownbtn = Button(self.resetax, 'Reset', color=self.axcolor, hovercolor='0.975')

        def increase_x(event):
            if ((self.spos.val + 0.5) <= (self.plot_xmax - self.swidth.val)):
                self.spos.set_val(self.spos.val + 0.5)
                update_pos(self.spos.val)

        def decrease_x(event):
            if ((self.spos.val - 0.5) >= self.plot_xmin):
                self.spos.set_val(self.spos.val - 0.5)
                update_pos(self.spos.val)

        def increase_xmax(event):
            if ((self.swidth.val + 0.5) <= self.plot_xmax):
                self.swidth.set_val(self.swidth.val + 0.5)
                update_width(self.swidth.val)

        def decrease_xmax(event):
            if ((self.swidth.val - 0.5) >= self.plot_xmin):
                self.swidth.set_val(self.swidth.val - 0.5)
                update_width(self.swidth.val)

        self.xleftbtn.on_clicked(decrease_x)
        self.xrightbtn.on_clicked(increase_x)
        self.xmaxleftbtn.on_clicked(decrease_xmax)
        self.xmaxrightbtn.on_clicked(increase_xmax)

        # I'm not sure how to detach these without them forgetting their parents (sliders)
        def update_pos(val):
            pos = self.spos.val
            width = self.swidth.val

            self.ax.axis([pos, pos + width, self.plot_ymin, self.plot_ymax])

        def update_width(val):
            pos = self.spos.val
            width = self.swidth.val

            if pos > (self.plot_xmax - width):
                pos = self.plot_xmax - width

            self.axpos.clear()
            self.spos.__init__(self.axpos, 'x', 0, self.plot_xmax - width, valinit=pos, valstep=0.5)
            self.spos.on_changed(update_pos)

            self.ax.axis([pos, pos + width, self.plot_ymin, self.plot_ymax])

            # TODO: Update
            # visible_average = calculate_average_midpoint_multiple_intervals(self.data, all_hold_times, i, i+width) * 1000
            # all_average = calculate_average_midpoint_multiple_intervals(self.data, all_hold_times, min(xdata), max(xdata)) * 1000

            # self.axes.set_title("Visible average: %.6f mA;\n Total average: %.6f mA." % (visible_average, all_average))

            # self.fig.canvas.draw_idle()

        self.spos.on_changed(update_pos)
        self.swidth.on_changed(update_width)

        def reset(event):
            self.swidth.reset()

            width = self.swidth.val
            self.axpos.clear()
            self.spos.__init__(self.axpos, 'x', 0, self.plot_xmax - width, valinit=0, valstep=0.5)
            self.spos.on_changed(update_pos)
            self.spos.reset()


            # TODO: Update parameters
            # visible_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, i, i+width) * 1000
            # all_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, min(xdata), max(xdata)) * 1000

            # self.axes.set_title("Visible average: %.6f mA;\n Total average: %.6f mA." % (visible_average, all_average))

        self.resetbtn.on_clicked(reset)

        self.spos.set_val(0)
        self.swidth.set_val(self.plot_xmax)

    def update_plot(self, data):
        verbose = self.verbose

        if data is None:
            if verbose: print("dgilib_plot.update_plot: Expected 'data', got an empty object.")
            return

        # In this if, the smart DGILibData object tests if it has data inside
        # TODO: Make 'if data: return' work for if data has no actual values in it.
        # ... Right now is if it has no interfaces.
        if (not data):
            if verbose: print("dgilib_plot.update_plot: Expected 'data' containing interfaces. Got 'data' with no interfaces. Returning from call with no work done.")
            return
        if (not data.power):
            if verbose: print("dgilib_plot.update_plot: Expected 'data' containing power data. Got 'data' with interfaces but no power timestamp & value pairs. Returning from call with no work done.")
            return
        if (not data.gpio):
            if verbose: print("dgilib_plot.update_plot: Expected 'data' containing gpio data. Got 'data' with interfaces but no gpio timestamp & value pairs.")
            return

        print(str(data))

        if not plt.fignum_exists(self.fig.number):
            plt.show()
        else:
            plt.draw()
            plt.pause(self.plot_pause_secs)

        for pin_idx in range(len(self.plot_pins)):

            if self.plot_pins[pin_idx] == True:

                hold_times_intervals = identify_hold_times(data,
                    self.plot_pins[pin_idx],
                    pin_idx,
                    correction_forward = self.pins_correction_forward,
                    shrink = self.pins_interval_shrink)

                for hold_time_interval in hold_times_intervals:
                    self.ax.axvspan(hold_time_interval[0], hold_time_interval[1], color=self.plot_pins_colors[pin_idx], alpha=0.5)

                    self.hold_times.append((hold_time_interval[0], hold_time_interval[1]))
                    self.hold_times_sum += hold_time_interval[1] - hold_time_interval[0]

        self.ln.set_xdata(data.power.timestamps)
        self.ln.set_ydata(data.power.values)

        pos = self.spos.val
        width = self.swidth.val

        #print("Scaling: " + str([pos, pos + width, self.plot_ymin, self.plot_ymax]))
        self.ax.axis([pos, pos + width, self.plot_ymin, self.plot_ymax])

        # visible_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, i, i+width) * 1000
        # all_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, min(xdata), max(xdata)) * 1000
        plt.pause(self.plot_pause_secs)

        self.draw_pins()

    def draw_pins(self,
                    default_plot_pins_method="highlight",
                    default_average_function="leftpoint"):

        plot_pins = None
        plot_pins_values = None
        plot_pins_method = None
        average_function = None

        if self.plot_pins is None: plot_pins=self.plot_pins
        if self.plot_pins_values is None: plot_pins_values=self.plot_pins_values
        if self.plot_pins_method is None: plot_pins_method=self.plot_pins_method
        if self.average_function is None: average_function=self.average_function
            
        verbose=self.verbose

        no_of_pins = len(self.plot_pins)

        if plot_pins is None:
            return []
        else:
            if (plot_pins_method is not "highlight") and (plot_pins_method is not "wave"):
                if (verbose): 
                    print("dgilib_plot.draw_pins: \"" + plot_pins_method + "\" is not a valid value for argument 'plot_pins_method'. Forcing the argument to value: + \"" + default_plot_pins_method + "\".")
                plot_pins_method = default_plot_pins_method

        if (average_function is not "leftpoint") and (average_function is not "midpoint"):
            if verbose: 
                print("dgilib_plot.draw_pins + \"" + average_function + "\" is not a valid value for argument 'average_function'. Forcing the ")
            average_function = default_average_function

        if (plot_pins is None) or (plot_pins == []):
            if verbose: 
                print("dgilib_plot.draw_pins: \"plot_pins\" argument missing. Information about what pins to plot is not available.")
            return []

        if (plot_pin_values is None) or (plot_pin_values == []):
            if verbose: 
                print("dgilib_plot.draw_pins: \"plot_pin_values\" argument missing. Information about what values to compare the pins to is not available.")
            return

        if plot_pins_method == "highlight":
            for pin_idx in range(no_of_pins): # For every pin number (0,1,2,3)
                if plot_pins[pin_idx] == True: # If we want them plotted
                    for hold_times in identify_hold_times(data, plot_pins[pin_idx], pin_idx, correction_forward = pins_correction_forward, shrink = pins_interval_shrink):
                        axes.axvspan(hold_times[0], hold_times[1], color=pins_colors[pin_idx], alpha=0.5)

                        #hold_times.append((hold_times[0], hold_times[1]))
                        #hold_times_sum += hold_times[1] - hold_times[0]
        else:
            pass
            # To be implemented


    def plot_still_exists(self):
        return plt.fignum_exists(self.fig.number)

    def plot_pause(self):
        plt.pause(self.plot_pause_secs)

    def keep_plot_alive(self):
        while self.plot_still_exists():
            self.plot_pause()


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

# Give it an index to continue from, so it does not go through all the data
def identify_hold_times(data, true_false, pin, correction_forward=0.00, shrink=0.00):
    if len(data.gpio.timestamps) <= 1: return [] # We can't identify intervals with only one value

    hold_times = []
    start = data.gpio.timestamps[0]
    end = data.gpio.timestamps[0]
    in_hold = true_false
    not_in_hold = not true_false
    search = not true_false

    #interval_sizes = []

    for i in range(len(data.gpio.timestamps)):
        if search == not_in_hold:  # Searching for start of hold time
            if data.gpio.values[i][pin] == search:
                start = data.gpio.timestamps[i]
            else:
                end = data.gpio.timestamps[i]
                search = not search

        if search == in_hold:  # Searching for end of hold time
            if data.gpio.values[i][pin] == search:
                end = data.gpio.timestamps[i]
            else:
                search = not search
                to_add = (start + correction_forward + shrink, end + correction_forward - shrink)
                if ((to_add[0] != to_add[1]) and (to_add[0] < to_add[1])):
                    hold_times.append(to_add)
                    #interval_sizes.append(to_add[1] - to_add[0])
                start = data.gpio.timestamps[i]

    should_add_last_interval = True
    for ht in hold_times:
        if (ht[0] == start): should_add_last_interval = False

    if should_add_last_interval:

        invented_end_time = data.power.timestamps[-1] + correction_forward - shrink

        # This function ASSUMES that the intervals are about the same in size.
        # ... If the last interval that should be highlighted on the graph is
        # ... abnormally higher than the maximum of the ones that already happened 
        # ... correctly then cancel highlighting with the help of 'invented_end_time' 
        # ... and highlight using the minimum from the 'interval_sizes' list, to get
        # ... an average that is most likely unaffected by stuff happening at the end
        # ... of the interval, which the power interface from the board failed to
        # ... communicate to us.
        # if ((invented_end_time - start) > max(interval_sizes)):
        #     invented_end_time = start + min(interval_sizes)

        to_add = (start + correction_forward + shrink, invented_end_time)

        if ((to_add[0] != to_add[1]) and (to_add[0] < to_add[1])):
            hold_times.append(to_add)

    return hold_times


def calculate_average_midpoint_single_interval(power_data, start_time=None, end_time=None):
    # Calculate average value using midpoint Riemann sum
    sum = 0

    actual_start_time = -1
    actual_end_time = -1

    for i in range(len(power_data[0]) - 1)[1:]:
        first_current_value = power_data[1][i]
        second_current_value = power_data[1][i + 1]
        timestamp = power_data[0][i + 1]
        last_time = power_data[0][i]

        if ((last_time >= start_time) and (last_time < end_time)):
            sum += ((first_current_value + second_current_value) / 2) * (timestamp - last_time)

            # We have to select the actual start time and the actual 
            if (actual_start_time == -1): actual_start_time = power_data[0][i]

        if (timestamp >= end_time):
            actual_end_time = power_data[0][i - 1]
            break

    return sum / (actual_end_time - actual_start_time)


def calculate_average_midpoint_multiple_intervals(power_data, intervals, start_time=None, end_time=None):
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
