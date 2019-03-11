from time import sleep
import csv

from pydgilib_extra.dgilib_extra_config import *
from pydgilib_extra.dgilib_calculations import identify_hold_times

import matplotlib.pyplot as plt; plt.ion()
from matplotlib.widgets import Slider, Button, TextBox

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
            self.ln, = self.ax.plot([], [], 'r-', label="Power")
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
            self.plot_ymax = 0.005
        else:
            self.plot_yauto = False

        self.plot_pins = kwargs.get("plot_pins", None)
        self.plot_pins_values = kwargs.get("plot_pins_values", None)
        self.plot_pins_method =  kwargs.get("plot_pins_method", "highlight")
        self.plot_pins_colors =  kwargs.get("plot_pins_colors", ["red", "orange", "blue", "green"])
        self.average_function =  kwargs.get("average_function", "leftpoint")
        self.axvspans = []

        # We need this since pin toggling is not aligned with power values changing when blinking a LED on the board, for example
        self.plot_pins_correction_forward = kwargs.get("plot_pins_correction_forward", 0.00075)
        self.plot_pins_interval_shrink = kwargs.get("plot_pins_interval_shrink", 0.0010)
        self.refresh_plot_pause_secs = kwargs.get("refresh_plot_pause_secs", 0.00000001)

        if self.plot_pins_method == "line":
            self.ax_pins = self.ax.twinx()
            self.ax_pins.set_ylabel('Pin Value')
            self.ax_pins.set_ylim([-0.1, 1.1])
            self.ax_pins.set_yticks([0,1])
            self.ax_pins.set_yticklabels(["Low", "High"])
            self.ln_pins = list(self.plot_pins) # Instantiate as copy of plot_pins
            for pin, plot_pin in enumerate(self.plot_pins):
                if plot_pin:
                    self.ln_pins[pin] = self.ax_pins.plot([], [], label=f"gpio{pin}")[0]
            self.ax_pins.legend(handles=[ln_pin for ln_pin in self.ln_pins if not isinstance(
                ln_pin, bool)] + [self.ln])  # Should actually check if it is a lines instance

        # Hardwiring these values to 0
        self.plot_xmin = 0
        self.plot_ymin = 0

        # We absolutely need these values from the user (or from the superior class), hence no default values
        # TODO: Are they really needed though?
        self.plot_xdiv = kwargs.get("plot_xdiv", min(5, self.plot_xmax))
        self.plot_xstep = kwargs.get("plot_xstep", 0.5)
        # self.duration = kwargs.get("duration", max(self.plot_xmax, 5))

        # We'll have some sliders to zoom in and out of the plot, as well as a cursor to move around when zoomed in
        # Leave space for sliders at the bottom
        plt.subplots_adjust(bottom=0.3)
        # Show grid
        self.ax.grid()

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
        self.hold_times_next_index = 0 # Will be incremented to 0 later
        self.hold_times_already_drawn = []

        self.verbose = kwargs.get("verbose", 0)

        self.initialize_sliders()

    def initialize_sliders(self):
        self.axpos = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=self.axcolor)
        self.axwidth = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=self.axcolor)
        self.resetax = plt.axes([0.8, 0.025, 0.1, 0.04])

        self.spos = Slider(self.axpos, 'x', 0, self.plot_xmax - self.plot_xdiv, valinit=0, valstep=self.plot_xstep)
        self.swidth = Slider(self.axwidth, 'xmax', 0, self.plot_xmax, valinit=self.plot_xdiv, valstep=self.plot_xstep)
        self.resetbtn = Button(self.resetax, 'Reset', color=self.axcolor, hovercolor='0.975')

        self.xleftax = plt.axes([0.4, 0.025, 0.095, 0.04])  # x_pos, y_pos, width, height
        self.xrightax = plt.axes([0.5, 0.025, 0.095, 0.04])
        self.xmaxleftax = plt.axes([0.6, 0.025, 0.095, 0.04])
        self.xmaxrightax = plt.axes([0.7, 0.025, 0.095, 0.04])
        self.xstepupax = plt.axes([0.3, 0.025, 0.095, 0.04])
        self.xstepdownax = plt.axes([0.2, 0.025, 0.095, 0.04])

        self.xleftbtn = Button(self.xleftax, '<x', color=self.axcolor, hovercolor='0.975')
        self.xrightbtn = Button(self.xrightax, 'x>', color=self.axcolor, hovercolor='0.975')
        self.xmaxleftbtn = Button(self.xmaxleftax, 'xmax-', color=self.axcolor, hovercolor='0.975')
        self.xmaxrightbtn = Button(self.xmaxrightax, 'xmax+', color=self.axcolor, hovercolor='0.975')
        self.xstepupbtn = Button(self.xstepupax, 'xstep+', color=self.axcolor, hovercolor='0.975')
        self.xstepdownbtn = Button(self.xstepdownax, 'xstep-', color=self.axcolor, hovercolor='0.975')

        self.xstepax = plt.axes([0.1, 0.025, 0.095, 0.04])
        self.xsteptb = TextBox(self.xstepax, 'xstep', initial=str(self.plot_xstep))

        def xstep_submit(text):
            self.plot_xstep = float(text)

        self.xsteptb.on_submit(xstep_submit)

        def increase_x(event):
            if ((self.spos.val + self.plot_xstep) <= (self.plot_xmax - self.swidth.val)):
                self.spos.set_val(self.spos.val + self.plot_xstep)
                update_pos(self.spos.val)

        def decrease_x(event):
            if ((self.spos.val - self.plot_xstep) >= (self.plot_xmin)):
                self.spos.set_val(self.spos.val - self.plot_xstep)
                update_pos(self.spos.val)

        def increase_xmax(event):
            if ((self.swidth.val + self.plot_xstep) <= self.plot_xmax):
                self.swidth.set_val(self.swidth.val + self.plot_xstep)
                update_width(self.swidth.val)

        def decrease_xmax(event):
            if ((self.swidth.val - self.plot_xstep) >= (self.plot_xmin + 0.000001)):
                self.swidth.set_val(self.swidth.val - self.plot_xstep)
                update_width(self.swidth.val)

        def increase_xstep(event):
            val = float(self.xsteptb.text)
            if ((val + 0.05) < (self.swidth.val - 0.000001)):
                self.xsteptb.set_val("{0:.2f}".format(val + 0.05))
                xstep_submit(self.xsteptb.text)
        
        def decrease_xstep(event):
            val = float(self.xsteptb.text)
            if ((val - 0.05) >= (0.05)):
                self.xsteptb.set_val("{0:.2f}".format(val - 0.05))
                xstep_submit(self.xsteptb.text)

        self.xleftbtn.on_clicked(decrease_x)
        self.xrightbtn.on_clicked(increase_x)
        self.xmaxleftbtn.on_clicked(decrease_xmax)
        self.xmaxrightbtn.on_clicked(increase_xmax)
        self.xstepupbtn.on_clicked(increase_xstep)
        self.xstepdownbtn.on_clicked(decrease_xstep)

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
            self.swidth.set_val(self.plot_xmax)

            #width = self.plot_xmax
            self.axpos.clear()
            self.spos.__init__(self.axpos, 'x', 0, self.plot_xmax, valinit=0, valstep=self.plot_xstep)
            self.spos.on_changed(update_pos)
            #self.spos.reset()


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

        if not plt.fignum_exists(self.fig.number):
            plt.show()
        else:
            plt.draw()
            self.refresh_plot(0.00000001)

        self.ln.set_xdata(data.power.timestamps)
        self.ln.set_ydata(data.power.values)

        pos = self.spos.val
        width = self.swidth.val

        #print("Scaling: " + str([pos, pos + width, self.plot_ymin, self.plot_ymax]))
        self.ax.axis([pos, pos + width, self.plot_ymin, self.plot_ymax])

        # visible_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, i, i+width) * 1000
        # all_average = calculate_average_midpoint_multiple_intervals([xdata,ydata], all_hold_times, min(xdata), max(xdata)) * 1000
        self.refresh_plot(0.00000001)

        self.draw_pins(data)
    
    def clear_pins(self):
        if self.axvspans is None: return
        
        for axvsp in self.axvspans:
            axvsp.remove()


    def draw_pins(self, data):
        # Here we set defaults (with or ...)
        ax = self.ax
        plot_pins = self.plot_pins
        plot_pins_values = self.plot_pins_values
        plot_pins_method = self.plot_pins_method or "highlight"
        plot_pins_correction_forward = self.plot_pins_correction_forward or 0.00
        plot_pins_interval_shrink = self.plot_pins_interval_shrink or 0.00
        plot_pins_colors = self.plot_pins_colors
        average_function = self.average_function or "leftpoint"

        # Here we do checks and stop drawing pins if something is unset
        if ax is None:                                      return
        if plot_pins is None:                               return
        if plot_pins_values is None:                        return
        if plot_pins_method is None:                        return
        if plot_pins_correction_forward is None:            return
        if plot_pins_interval_shrink is None:               return
        if plot_pins_colors is None:                        return
        if average_function is None:                        return
            
        verbose=self.verbose

        no_of_pins = len(self.plot_pins)

        if plot_pins_method == "highlight":

            for pin_idx in range(no_of_pins): # For every pin number (0,1,2,3)

                if plot_pins[pin_idx] == True: # If we want them plotted
                    
                    if len(self.hold_times_already_drawn) > 0:
                        last_processed_index = data.gpio.timestamps.index(self.hold_times_already_drawn[-1][-1])
                    else:
                        last_processed_index = 0
                        
                    hold_times = identify_hold_times(data,
                                                    pin_idx,
                                                    plot_pins_values[pin_idx],
                                                    start_index=(last_processed_index + 1))

                    for ht in hold_times:
                        axvsp = ax.axvspan(ht[0], ht[1], color=plot_pins_colors[pin_idx], alpha=0.5)
                        self.axvspans.append(axvsp)
                        if ht not in self.hold_times_already_drawn:
                            self.hold_times_already_drawn.append(ht)
            #self.hold_times_next_index = len(data.gpio.timestamps)
            #hold_times.append((hold_times[0], hold_times[1]))
            #hold_times_sum += hold_times[1] - hold_times[0]
        elif self.plot_pins_method == "line":
            for pin, plot_pin in enumerate(self.plot_pins):
                if plot_pin:
                    self.ln_pins[pin].set_xdata(data.gpio.timestamps)
                    self.ln_pins[pin].set_ydata(
                        data.gpio.get_select_in_value(pin))
            self.fig.show()
        else:
            raise ValueError(f"Unrecognized plot_pins_method: {self.plot_pins_method}")

    def plot_still_exists(self):
        return plt.fignum_exists(self.fig.number)

    def refresh_plot(self, time=None):
        self.ax.relim()                  # recompute the data limits
        self.ax.autoscale_view()         # automatic axis scaling
        self.fig.canvas.flush_events() 
        #sleep(time or self.refresh_plot_pause_secs)
        #plt.pause(self.plot_pause_secs)

    def keep_plot_alive(self):
        while self.plot_still_exists():
            self.refresh_plot()

# Obsolete
# Give it an index to continue from, so it does not go through all the data
# def identify_hold_times(data, start_index, true_false, pin, correction_forward=0.00, shrink=0.00):
#     if len(data.gpio.timestamps) <= 1: return [] # We can't identify intervals with only one value

#     hold_times = []
#     start = data.gpio.timestamps[0]
#     end = data.gpio.timestamps[0]
#     in_hold = true_false
#     not_in_hold = not true_false
#     search = not true_false

#     #interval_sizes = []

#     #print("Start index: " + str(start_index))

#     for i in range(start_index, len(data.gpio.timestamps)):
#         if search == not_in_hold:  # Searching for start of hold time
#             if data.gpio.values[i][pin] == search:
#                 start = data.gpio.timestamps[i]
#             else:
#                 end = data.gpio.timestamps[i]
#                 search = not search

#         if search == in_hold:  # Searching for end of hold time
#             if data.gpio.values[i][pin] == search:
#                 end = data.gpio.timestamps[i]
#             else:
#                 search = not search
#                 to_add = (start + correction_forward + shrink, end + correction_forward - shrink)
#                 if ((to_add[0] != to_add[1]) and (to_add[0] < to_add[1])):
#                     hold_times.append(to_add)
#                     #interval_sizes.append(to_add[1] - to_add[0])
#                 start = data.gpio.timestamps[i]

#     # should_add_last_interval = True
#     # for ht in hold_times:
#     #     if (ht[0] == start): should_add_last_interval = False

#     # if should_add_last_interval:

#     #     invented_end_time = data.power.timestamps[-1] + correction_forward - shrink

#     #     # This function ASSUMES that the intervals are about the same in size.
#     #     # ... If the last interval that should be highlighted on the graph is
#     #     # ... abnormally higher than the maximum of the ones that already happened 
#     #     # ... correctly then cancel highlighting with the help of 'invented_end_time' 
#     #     # ... and highlight using the minimum from the 'interval_sizes' list, to get
#     #     # ... an average that is most likely unaffected by stuff happening at the end
#     #     # ... of the interval, which the power interface from the board failed to
#     #     # ... communicate to us.
#     #     # if ((invented_end_time - start) > max(interval_sizes)):
#     #     #     invented_end_time = start + min(interval_sizes)

#     #     to_add = (start + correction_forward + shrink, invented_end_time)

#     #     if ((to_add[0] != to_add[1]) and (to_add[0] < to_add[1])):
#     #         hold_times.append(to_add)
    
#     # A smart printing for debugging this function
#     # Either leave 'debug = False' or comment it, but don't lose it
#     debug = False
#     if debug:
#         ht_zip = list(zip(*hold_times))
#         for (t, v) in data.gpio:
#             #print(str((t,v)))
#             if t in ht_zip[0]:
#                 print("\t" + str(t) + "\t\t" + str(v) + "\t <-- start")
#             elif t in ht_zip[1]:
#                 print("\t" + str(t) + "\t\t" + str(v) + "\t <-- stop")
#             else:
#                 print("\t" + str(t) + "\t\t" + str(v))

#     return hold_times

# Obsolete
# def shift_data(data, shift_by):
#     new_data = copy.deepcopy(data)

#     for i in range(len(data[INTERFACE_POWER][0])):
#         new_data[INTERFACE_POWER][0][i] = shift_by + data[INTERFACE_POWER][0][i]

#     for i in range(len(data[INTERFACE_GPIO][0])):
#         new_data[INTERFACE_GPIO][0][i] = shift_by + data[INTERFACE_GPIO][0][i]

#     return new_data
