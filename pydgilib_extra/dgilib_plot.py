from time import sleep
import csv
import sys

from pydgilib_extra.dgilib_extra_config import *
from pydgilib_extra.dgilib_calculations import StreamingCalculation
#from tests_plot.dgilib_averages import HoldTimes

import matplotlib.pyplot as plt; plt.ion()
import matplotlib
from matplotlib.widgets import Slider, Button, TextBox

from threading import Lock

float_epsilon = sys.float_info.epsilon

class HoldTimes(StreamingCalculation):

    def identify_toggle_times(self, pin, data_gpio=None, gpio_start_index=0):
        if data_gpio is None:
            data_gpio = self.data
        if gpio_start_index == None:
            gpio_start_index = self.index

        if len(data_gpio.timestamps) <= 1:
            return []  # We can't identify intervals with only one value
        if gpio_start_index > (len(data_gpio.timestamps) - 1):
            return []  # We're being asked to do an index that does not exist yet, so just skip

        toggle_times = []
        true_to_false_toggle_times = []
        false_to_true_toggle_times = []

        #last_toggle_timestamp = data_gpio.timestamps[start_index]
        last_toggle_value = data_gpio.values[gpio_start_index][pin]

        #print("New data, starting on pin " + str(pin) + " at timestamp " + str(data_gpio.timestamps[start_index]) + " of value " + str(last_toggle_value) + ". Index is: " + str(start_index))

        for i in range(gpio_start_index, len(data_gpio)):
            if last_toggle_value != data_gpio.values[i][pin]:
                #print("Detected toggle on pin " + str(pin) + " at timestamp " + str(data_gpio.timestamps[i]) + " of value " + str(data_gpio.values[i][pin]) + ". Index is: " + str(i))
                toggle_times.append(data_gpio.timestamps[i])
                if last_toggle_value == True:
                    true_to_false_toggle_times.append(data_gpio.timestamps[i])
                if last_toggle_value == False:
                    false_to_true_toggle_times.append(data_gpio.timestamps[i])

                #last_toggle_timestamp = data_gpio.timestamps[i]
                last_toggle_value = data_gpio.values[i][pin]

        # A smart printing for debugging this function
        # Either leave 'debug = False' or comment it, but don't lose it
        debug = False
        if debug:
            for (t, v) in data_gpio:
                # print(str((t,v)))
                if t in toggle_times:
                    print("\t" + str(t) + "\t\t" + str(v) + "\t <-- toggled")
                else:
                    print("\t" + str(t) + "\t\t" + str(v))

        # , last_toggle_index
        return toggle_times, true_to_false_toggle_times, false_to_true_toggle_times

    def identify_hold_times(self, pin, pin_value, data_gpio=None):
        if data_gpio is None:
            data_gpio = self.data
        if len(data_gpio.timestamps) <= 1:
            return []  # We can't identify intervals with only one value
        if self.index > (len(data_gpio.timestamps) - 1):
            return []  # We're being asked to do an index that does not exist yet, so just skip

        hold_times = []

        (_, true_to_false_times, false_to_true_times) = self.identify_toggle_times(
            pin, data_gpio, self.index)

        #print("T2F: " + str(true_to_false_times))
        #print("F2T: " + str(false_to_true_times))

        if len(false_to_true_times) == 0:
            return
        if len(true_to_false_times) == 0:
            return

        if (pin_value == True):
            # A fix
            if false_to_true_times[0] > true_to_false_times[0]:
                true_to_false_times.pop(0)
            hold_times = zip(false_to_true_times, true_to_false_times)
        elif (pin_value == False):
            # A fix
            if true_to_false_times[0] > false_to_true_times[0]:
                false_to_true_times.pop(0)
            hold_times = zip(true_to_false_times, false_to_true_times)

        # A smart printing for debugging this function
        # Either leave 'debug = False' or comment it, but don't lose it
        debug = False
        if debug:
            ht_zip = list(zip(*hold_times))
            for (t, v) in data_gpio:
                # print(str((t,v)))
                if t in ht_zip[0]:
                    print("\t" + str(t) + "\t\t" + str(v) + "\t <-- start")
                elif t in ht_zip[1]:
                    print("\t" + str(t) + "\t\t" + str(v) + "\t <-- stop")
                else:
                    print("\t" + str(t) + "\t\t" + str(v))

        hold_times_list = list(hold_times)

        try:
            self.index = data_gpio.timestamps.index(
                hold_times_list[-1][-1]) + 1
        except IndexError:
            # If you remove this, you get an error
            pass

        return hold_times_list

class DGILibPlot(object):
    """DGILibPlot
   
    The `DGILibPlot` class is responsible with plotting the electrical current
    (Amperes) data and gpio state data (values of `1`/`0`) obtained from an
    Atmel board.

    The X axis represents time in seconds, while the Y axis represents
    the electrical current in Amperes.

    There are two ways that the gpio pins state can be shown along with the
    electrical current. One is the `line` method and one is the `highlight`
    method. The `line` method shows a square waveform, a typical byproduct of
    the digital signal that gpio pins usually have. The `highlight` method
    highlights only particular parts of the plot with semi-transparent
    coloured areas, where the pins have a value of interest (set using the
    ``plot_pins_values`` argument of the class).

    Below are shown some examples of `DGILibPlot` and the two methods of
    drawing the gpio pins  (`line`/`highlight`).

    **Example plots using "line" method:**

    .. figure:: images/plot_line_1.png
       :scale: 60%

       Figure 1: Example of plot with the 'line' method chosen for the drawing of
       pins. All of the pins are being plotted, so you can always see their
       `True`/`False` values.

    .. figure:: images/plot_line_2.png
       :scale: 60%

       Figure 2: The same plot with the same data as figure 1, only zoomed in.

    .. figure:: images/plot_line_3.png
       :scale: 60%

       Figure 3: The same plot with the same data as figure 1 and 2, only even
       more zoomed in. Here we can clearly see that gpio pins 0, 2 and 3 have
       defaulted on a single value all along the program's execution on the
       board. We can however clearly see the toggling of pin 1,
       represented in orange.

    **Example plots using "highlight" method:**

    .. figure:: images/plot_highlight_1.png
       :scale: 60%

       Figure 4: Example of plot with the 'highlight' method chosen for the
       drawing of pins. The time the pins are holding the value of interest (in
       this case, `True` value) is small every time. This is why we can see the
       highlighted areas looking more like vertical lines when zoomed
       out. The only pin being toggled by the program on the board is
       pin 1, hence it's why we only see one color of highlighted areas.

    .. figure:: images/plot_highlight_2.png
       :scale: 60%

       Figure 5: The same plot with the same data as figure 1, only zoomed in.

    .. figure:: images/plot_highlight_3.png
       :scale: 60%

       Figure 6: The same plot with the same data as figure 1 and 2, only even
       more zoomed in. Now we can see one of the the  highlight
       area in its proper form.

    **Parameters**

    The parameters listed in the section below can be passed as arguments when
    initializing the `DGILibPlot` object, or as arguments to a `DGILibExtra`
    object. They can be included in a configuration dictionary
    (:py:class:`dict` object) and then unwrapped in the initialization function
    call of either the `DGILibPlot` object or the `DGILibExtra` object (by
    doing: ``dgilib_plot = DGILibPlot(**config_dict)`` or ``with
    DGILibExtra(**config_dict) as dgilib: ...``).

    Parameters
    ----------
    dgilib_extra : DGILibExtra
        A `DGILibExtra` object can be specified, from where the plot can obtain
        the electrical current and gpio state data. If a `DGILibExtra` object
        is not desired to be specified however, then it should be set to
        `None`.

        (the default is `None`, meaning that measurements data (in the form
        of a :class:`DGILibData` should be manually called as 
        function updates))

    fig : matplotlib.pyplot.figure, optional
        If it is wanted so that the data is to be plotted on an already
        existing `matplotlib` figure, then the object representing the already
        instantiated figure can be specified for this parameter. For example,
        the electrical current data and gpio state data can be plotted
        in a subplot of a figure window that holds other plots as well.

        (the default is `None`, meaning that a new figure object will be
        created internally)

    ax : matplotlib.pyplot.axes, optional
        If it is wanted so that the data is to be plotted on an already
        existing `matplotlib` axes, then the object representing the already
        instantiated axes can be specified for this parameter.

        (the default is `None`, meaning that a new axes object will be
        created internally)

    ln : matplotlib.pyplot.lines2d, optional
        If it is wanted so that the data is to be plotted on an already
        existing `matplotlib` `Lines2D` object, then the object representing
        the already instantiated `Lines2D` object can be specified for this
        parameter.

        (the default is `None`, meaning that a new `Lines2D` object will be
        created internally)

    window_title : str, optional
        If another window title than the default is desired to be used, it can
        be specified here.

        (the default is ``Plot of current (in amperes) and gpio pins``)

    plot_xmax : int, optional
        This *initializes* the figure view to a maximum of `plot_xmax` on
        the X axis, where the data to be plotted. Later, the user can change
        the figure view using the bottom sliders of the plot figure.

        (the default is an arbitrary `10`)

    plot_ymax : int, optional
        This *initializes* the figure view to a maximum of `plot_xmax` on
        the Y axis, where the data to be plotted. Later, the user can change
        the figure view using the bottom sliders of the plot figure.

        (the default is `0.005`, meaning 5 mA, so that something as
        energy consuming as a blinking LED can be shown by a `DGILibPlot`
        with default settings)

    plot_pins : list(bool, bool, bool, bool), optional
        Set the pins to be drawn in the plot, out of the 4 GPIO available pins
        that the Atmel board gives data about to be sent through the computer
        through the Atmel Embedded Debugger (EDBG) Data Gateway Interface
        (DGI).

        (the default is `[True, True, True, True]`, meaning all pins are
        drawn)

    plot_pins_method : str, optional
        Set the *method* of drawing the pin. The values can be either
        ``"line"`` or ``"highlight"``. Refer to the above figures to see
        the differences.

        (the default is `"highlight"`)

    plot_pins_colors : list(str, str, str, str), optional
        Set the colors of the semi-transparent highlight areas drawn when using
        the `highlight` method, or the lines when using the `lines` method of
        drawing pins. 
        
        (the default is `["red", "orange", "blue", "green"]`,
        meaning that pin 0 will have a `red` semi-transparent highlight area or
        line, pin 1 will have `orange` ones, and so on)

    automove_method : str, optional
        When the plot is receiving data live from the measurements taken in
        real-time from the board (as opposed to receiving all the data to be
        plotted at once, say, when reading the data from saved csv files), and
        `plot_xmax` is smaller than the expected size of the data in the end,
        then at some point the data will update past the figure view.
        `DGILibPlot` automatically moves the figure view to the last timestamp
        of the latest data received, and it can do so in two ways, depending on
        the value of ``automove_method``.

        The `page` method changes the figure view in increments of
        ``plot_ymax``, when the data updates past the figure view, as if the
        plot is turning one "page" at a time. The `latest_data` method makes
        the figure view always have the latest data in view, meaning that it
        moves in small increments so that it always keeps the latest data point
        `0.15` seconds away from the right edge of the figure view. The `0.15`
        seconds value is an arbitrary hard-coded value, chosen after some
        experiments.

        (the default is 'latest_data', meaning the plot's figure view will
        follow the latest data in smaller increments, keeping the latest data
        always on the right side of the plot)

    verbose : int
        Specifies verbosity:

        - 0: Silent

        - 1: Currently prints if data is missing, either as an object or as \
        values, when :func:`update_plot` is being called.

        (the default is `0`)

    Attributes
    ----------
    axvspans : list(4 x list(matplotlib.pyplot.axvspan))
        The way the semi-transparent coloured areas for the gpio pins are drawn
        on the plot is by using ``matplotlib.pyplot.axvspan`` objects. The
        `axvspan` objects are collected in a list for potential use for later.
        (e.g.: such as to delete them, using the :func:`clear_pins` method).

        (the default is 4 empty lists, meaning no highlighting of areas of
        interest has occured yet)

    annotations : list(4 x list(str))
        As we have seen in figures 4, 5, 6, for the `highlight` method of
        drawing pins, the counting or iteration of the highlighted areas are
        also showed on the plot. There are 4 pins, so therefore 4 lists of the
        counting/iteration stored as strings are saved by the `DGILibPlot` for
        later use by developers (e.g.: to replace from numbers to actual
        descriptions and then call the redrawing of pins).

        (the default is 4 empty lists, meaning no annotations for the
        highlighted areas of interest were placed yet)

    preprocessed_averages_data : list(4 x list(tuple(int, \
    tuple(float, float), int, float)))
        As the `highlight` method draws the pins on the plot with the help of
        the :class:`HoldTimes` class, that means the plot knows afterwards the
        time intervals in which the pins have values of interest. This can be
        valuable for a subsequent averaging function that wants to calculate
        faster the average current or energy consumption of the the board
        activity only where it was highlighted on the plot. As such,
        `DGILibPlot` prepares a list of 4 lists of tuples, each for every pin,
        the tuple containing the iteration index of the highlighted area of
        interest the pins kept the same value consecutively (called a `hold`
        time), another tuple containing the timestamps with respect to the
        electrical current data, which says the beginning and end times of that
        `hold` interval,  an index in the list of the electrical current data
        points where the respective hold time starts and, lastly, a `None`
        value, which then should be replaced with a :py:class:`float` value for
        the the average current or charge during that hold time.

        (the default is 4 empty lists, meaning no gathered preprocessed
        averages data yet)

    iterations : list(4 x int)
        As the plot is being updated live, the `iterations` list holds the
        number of highlighed areas that have been drawn already for for each
        pin. As the whole measurement data gets plotted, the iterations list
        practically holds the number of iterations the of all the areas
        of interest for each pin (which can be, for example, the number
        of `for` loops that took place in the program itself running on the
        board).

        (the default are 4 ``0`` values, meaning no areas of interest
        on the gpio data has been identified)

    last_xpos : float
        As the plot is being updated live, the figure view moves along with the
        latest data to be shown on the plot. If the user desires to stop this
        automatic movement and focus on some specific area of the plot, while
        the data is still being updated in real-time, the figure needs to
        detect that it should stop following the data to not disturb the user.
        It does so by comparing the current x-axis position value of the x axis
        shown, with the last x-axis position value saved, before doing any
        automatic movement of the figure view. If they are different, no
        automatic movement is being done from now on.
        
    xylim_mutex : Lock
        As there are many ways to move, zoom and otherwise manipulate the
        figure view to different sections of the plot, using the `matplotlib`'s
        implicit movement and zoom controls, or the freshly built `DGILibPlot`
        sliders appearing at the bottom (See figures), or the automatic
        following of the latest data feature, there is a multi-threading aspect
        involved and therefore a mutex should be involved, in the form
        of a `Lock` object, to prevent anomalies.

    hold_times_obj: HoldTimes
        Only instantiated when `highlight` method is being used for drawing
        pins information, the :class:`HoldTimes` class holds the algorithm that
        works on the live data to obtain the timestamps of areas of interest of
        the gpio data, in order to be highlighted on the plot. As the algorithm
        works on live updating data, the areas of interst can be cut off
        between updates of data. As such, the :class:`HoldTimes` keeps
        information for the algorithm to work with, in order to advert this.    
    """

    def __init__(self, dgilib_extra=None, *args, **kwargs):
        self.dgilib_extra = dgilib_extra

        # Maybe the user wants to put the power figure along with 
        # other figures he wants
        self.fig = kwargs.get("fig")
        if self.fig is None:
            self.fig = plt.figure(figsize=(8, 6))
            
        # Set window title if supplied, if not set a default
        self.window_title = kwargs.get("window_title",
                                       "Plot of current (in amperes) and" +
                                       "gpio pins")
        self.fig.canvas.set_window_title(self.window_title)

        self.ax = kwargs.get("ax")
        if self.ax is None:
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.ax.set_xlabel('Time [s]')
            self.ax.set_ylabel('Current [A]')

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

        self.plot_pins = kwargs.get("plot_pins", [True, True, True, True])
        self.plot_pins_values = kwargs.get("plot_pins_values", [True, True, True, True])
        self.plot_pins_method = kwargs.get("plot_pins_method", "highlight") # or "line"
        self.plot_pins_colors = kwargs.get("plot_pins_colors", ["red", "orange", "blue", "green"])
        self.automove_method = kwargs.get("automove_method", "latest_data") # or "page"
        self.axvspans = [[], [], [], []]
        self.annotations = [[], [], [], []]
        self.preprocessed_averages_data = [[], [], [], []]
        #self.total_average = [0,0,0,0]
        self.iterations = [0,0,0,0]
        self.last_xpos = 0.0
        self.xylim_mutex = Lock()

        #self.refresh_plot_pause_secs = kwargs.get("refresh_plot_pause_secs", 0.00000001)

        if self.plot_pins_method == "highlight":
            self.hold_times_obj = HoldTimes()

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

        # We need these values from the user (or from the superior class), 
        #   hence no default values
        # TODO: Are they really needed though?
        self.plot_xdiv = kwargs.get("plot_xdiv", min(5, self.plot_xmax))
        self.plot_xstep = kwargs.get("plot_xstep", 0.5)
        self.plot_xstep_default = self.plot_xstep
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
        self.hold_times_sum = 0.00
        self.hold_times_next_index = 0 # Will be incremented to 0 later
        self.hold_times_already_drawn = []

        self.verbose = kwargs.get("verbose", 0)

        self.initialize_sliders()

    def initialize_sliders(self):
        self.axpos = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=self.axcolor)
        self.axwidth = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=self.axcolor)
        self.resetax = plt.axes([0.8, 0.025, 0.1, 0.04])

        self.spos = Slider(self.axpos, 'x', 0, self.plot_xmax, valinit=0, valstep=self.plot_xstep)
        self.swidth = Slider(self.axwidth, 'xmax', 0, self.plot_xmax, valinit=self.plot_xdiv, valstep=self.plot_xstep)
        self.resetbtn = Button(self.resetax, 'Reset', color=self.axcolor, hovercolor='0.975')

        #TODO: Change to pixel sizes
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
            #if ((self.spos.val + self.plot_xstep) <= (self.plot_xmax - self.swidth.val)):
            self.spos.set_val(self.spos.val + self.plot_xstep)
            update_pos(self.spos.val)

        def decrease_x(event):
            #if ((self.spos.val - self.plot_xstep) >= (self.plot_xmin)):
            self.spos.set_val(self.spos.val - self.plot_xstep)
            update_pos(self.spos.val)

        def increase_xmax(event):
            #if ((self.swidth.val + self.plot_xstep) <= self.plot_xmax):
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
            if self.xylim_mutex.acquire(False):
                pos = self.spos.val
                width = self.swidth.val

                #self.set_axis(pos, pos + width, self.plot_ymin, self.plot_ymax, "update_pos function")
                self.ax.axis([pos, pos + width, self.plot_ymin, self.plot_ymax])

                self.xylim_mutex.release()

        def update_width(val):
            if self.xylim_mutex.acquire(False):
                pos = self.spos.val
                width = self.swidth.val

                self.axpos.clear()
                self.spos.__init__(self.axpos, 'x', 0, width, valinit=pos, valstep=self.plot_xstep)
                self.spos.on_changed(update_pos)
                self.spos.set_val(pos)

                #self.set_axis(pos, pos + width, self.plot_ymin, self.plot_ymax, "update_width function")
                self.ax.axis([pos, pos + width, self.plot_ymin, self.plot_ymax])

                self.xylim_mutex.release()

        self.spos.on_changed(update_pos)
        self.swidth.on_changed(update_width)

        # TODO: This
        def see_all(event):
            if self.xylim_mutex.acquire(False):

                #self.set_axis(0, self.last_timestamp, self.plot_ymin, self.plot_ymax, "see_all function")
                self.ax.axis([0, self.last_timestamp, self.plot_ymin, self.plot_ymax])
                self.last_xpos = -1

                self.xylim_mutex.release()

        def reset(event):
            if self.xylim_mutex.acquire(False):
                self.swidth.set_val(self.plot_xmax)
                
                self.axpos.clear()
                self.spos.__init__(self.axpos, 'x', 0, self.plot_xmax, valinit=0, valstep=self.plot_xstep_default)
                self.spos.on_changed(update_pos)
        
                self.xsteptb.set_val(str(self.plot_xstep_default))

                #self.set_axis(self.plot_xmin, self.plot_xmax, self.plot_ymin, self.plot_ymax, "reset function")
                self.ax.axis([self.plot_xmin, self.plot_xmax, self.plot_ymin, self.plot_ymax])
                self.last_xpos = -1

                self.xylim_mutex.release()                

        self.resetbtn.on_clicked(reset)

        self.spos.set_val(0)
        self.swidth.set_val(self.plot_xmax)

        # Auto-change the sliders/buttons when using plot tools
        def on_xlims_change(axes):
            if self.xylim_mutex.acquire(False): # Non-blocking
                xlim_left = self.ax.get_xlim()[0]
                xlim_right = self.ax.get_xlim()[1]

                pos = xlim_left
                width = xlim_right - xlim_left

                self.spos.set_val(pos)
                self.swidth.set_val(width)
                self.last_xpos = -1
            
                self.xylim_mutex.release()

        def on_ylims_change(axes):
            print(self.ax.get_ylim())

        self.ax.callbacks.connect('xlim_changed', on_xlims_change)
        #self.ax.callbacks.connect('ylim_changed', on_ylims_change)

    def update_plot(self, data):
        verbose = self.verbose

        if data is None:
            data = self.dgilib_extra.data

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
        self.refresh_plot()

        #TODO: ln might have an update_callback and then it can listen to the data being updated instead of updating data here
        self.ln.set_xdata(data.power.timestamps)
        self.ln.set_ydata(data.power.values)

        automove = True
        current_xpos = self.ax.get_xlim()[0]

        if self.last_xpos != current_xpos:
            automove = False

        if automove and self.xylim_mutex.acquire(False):
            last_timestamp = data.power.timestamps[-1]

            pos = self.spos.val
            width = self.swidth.val
            
            if (last_timestamp > (pos + width)):
                if self.automove_method == "page":
                    self.spos.set_val(pos + width)
                elif self.automove_method == "latest_data":
                    arbitrary_amount = 0.15
                    if last_timestamp > width:
                        self.spos.set_val(last_timestamp + arbitrary_amount - width)

            pos = self.spos.val
            width = self.swidth.val

            self.ax.axis([pos, pos + width, self.plot_ymin, self.plot_ymax])
            self.last_xpos = pos

            self.xylim_mutex.release()

        self.refresh_plot()

        self.draw_pins(data)
    
    def clear_pins(self):
        """
        Clears the highlighted areas on the plot that represent the state of the gpio pins
        (as seen in figures 4, 5, 6). Using this method only makes sense if the `highlight`
        method of drawing pins was used.
        """
        if self.axvspans is None:
            return
        
        for axvsp in self.axvspans:
            axvsp.remove()

    def draw_pins(self, data):
        """draw_pins [summary]
        
        Raises
        ------
        ValueError
            Raised when `plot_pins_method` member of class has another 
            string value than the ones available (`highlight`, `line`)

        Parameters
        ----------
        data : DGILibData
            :class:`DGILibData` object that contains the GPIO data to be drawn
            on the plot.
        """
        # Here we set defaults (with 'or' keyword ...)
        ax = self.ax
        plot_pins = self.plot_pins
        plot_pins_values = self.plot_pins_values
        #plot_pins_method = self.plot_pins_method or "highlight"
        plot_pins_colors = self.plot_pins_colors

        # Here we do checks and stop drawing pins if something is unset
        if ax is None:                                      return
        if plot_pins is None:                               return
            
        verbose=self.verbose

        no_of_pins = len(self.plot_pins)

        if self.plot_pins_method == "highlight":

            for pin_idx in range(no_of_pins): # For every pin number (0,1,2,3)

                if plot_pins[pin_idx] == True: # If we want them plotted
                        
                    hold_times = self.hold_times_obj.identify_hold_times(pin_idx, plot_pins_values[pin_idx], data.gpio)

                    if hold_times is not None:
                        for ht in hold_times:
                            axvsp = ax.axvspan(ht[0], ht[1], color=plot_pins_colors[pin_idx], alpha=0.25)
                            self.axvspans[pin_idx].append(axvsp)

                            x_halfway = (ht[1] - ht[0]) / 4 + ht[0]
                            y_halfway = (self.plot_ymax - self.plot_ymin) / 2 + self.plot_ymin
                            annon = ax.annotate(str(self.iterations[pin_idx] + 1), xy=(x_halfway, y_halfway))
                            self.annotations[pin_idx].append(annon)
                            
                            self.iterations[pin_idx] += 1

                            # TODO:  The start and stop indexes of the data points that are area of interest
                            # might be more useful for an averaging function, but currently the plot uses
                            # the coordinates of the X axis(the start/stop timestamps) in order to highlight
                            # the areas of interest.
                            self.preprocessed_averages_data[pin_idx].append((self.iterations[pin_idx], ht, 0, None))
            
            # This should be in update_plot()
            self.ax.set_title(
                f"Logging. Collected {len(data.power)} power samples and {len(data.gpio)} gpio samples.")

        elif self.plot_pins_method == "line":
            extend_gpio = data.gpio.timestamps[-1] < data.power.timestamps[-1]
            for pin, plot_pin in enumerate(self.plot_pins):
                if plot_pin:
                    self.ln_pins[pin].set_xdata(
                        data.gpio.timestamps + extend_gpio * [data.power.timestamps[-1]])
                    self.ln_pins[pin].set_ydata(
                        data.gpio.get_select_in_value(pin) + extend_gpio * [data.gpio.values[-1][pin]])
            self.ax.set_title(f"Logging. Collected {len(data.power)} power samples and {len(data.gpio)} gpio samples.")
            self.fig.show()
        else:
            raise ValueError(f"Unrecognized plot_pins_method: {self.plot_pins_method}")

    def plot_still_exists(self):
        """plot_still_exists 
        
        Can be used in a boolean (e.g.: `if`, `while`) clause to check if the
        plot is still shown inside a window (e.g.: to unpause program
        functionality if the plot is closed).

        Also used in the :func:`keep_plot_alive` member function of the
        class.

        Returns
        -------
        bool
            Returns `True` if the plot still exists and `False` otherwise.
        """
        return plt.fignum_exists(self.fig.number)

    def refresh_plot(self):
        """refresh_plot

        Makes a few `matplotlib` specific calls to refresh and redraw the plot
        (especially when new data is to be drawn). 
        
        Is used in :func:`update_plot` member function of the class.
        """
        self.ax.relim()                  # recompute the data limits
        self.ax.autoscale_view()         # automatic axis scaling
        self.fig.canvas.flush_events() 

    def keep_plot_alive(self):
        while self.plot_still_exists():
            self.refresh_plot()
        """keep_plot_alive
        
        Pauses program functionality until the plot is closed. Does so
        by refreshing the plot using :func:`refresh_plot`.
        """

    def pause(self, time=0.000001):
        """pause

        Calls `matplotlib's` `pause` function for an amount of seconds.

        Parameters
        ----------
        time : float
            The number of seconds the plot should have time to refresh itself
            and pause program functionality.
        """
        plt.pause(time)

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
