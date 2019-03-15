# pylint: disable=E1101
"""This module wraps the logging functionality for DGILibExtra."""

import copy
from os import getcwd
from time import time

# Todo, remove dependency
# import matplotlib.pyplot as plt

from pydgilib.dgilib_config import INTERFACE_GPIO
from pydgilib_extra.dgilib_data import LoggerData
from pydgilib_extra.dgilib_extra_config import (
    INTERFACE_POWER, LOGGER_CSV, LOGGER_OBJECT, LOGGER_PLOT, FILE_NAME_BASE,
    POLLING, POWER)
from pydgilib_extra.dgilib_plot import DGILibPlot
from pydgilib_extra.dgilib_averages import DGILibAverages


class DGILibLogger(object):
    """Wraps the logging functionality for DGILibExtra.

    Interfaces:
        - GPIO mode
        - Power mode
    """

    def __init__(self, *args, **kwargs):
        """Instantiate DGILibInterfacePower object."""
        self.dgilib_extra = kwargs.get(
            "dgilib_extra", args[0] if args else None)

        # Get enabled loggers
        self.loggers = kwargs.get("loggers", [])

        # Enable the csv logger if file_name_base or log_folder has been
        # specified.
        if LOGGER_CSV not in self.loggers and ("file_name_base" in kwargs or
                                               "log_folder" in kwargs):
            self.loggers.append(LOGGER_CSV)

        # file_name_base - merely the optional base of the filename
        #     (Preferably leave standard).
        # log_folder - where log files will be saved
        self.file_name_base = kwargs.get("file_name_base", FILE_NAME_BASE)
        self.log_folder = kwargs.get("log_folder", getcwd())

        # Enable the plot logger if figure has been specified.
        if (LOGGER_PLOT not in self.loggers and
                ("fig" in kwargs or "ax" in kwargs)):
            self.loggers.append(LOGGER_PLOT)

        # Set self.figure if LOGGER_PLOT enabled
        # Create axes self.axes if LOGGER_PLOT is enabled
        if LOGGER_PLOT in self.loggers:
            self.plotobj = DGILibPlot(self.dgilib_extra, *args, **kwargs)
            self.refresh_plot = self.plotobj.refresh_plot
            self.plot_still_exists = self.plotobj.plot_still_exists
            self.keep_plot_alive = self.plotobj.keep_plot_alive

            # Force logging in object if logging in plot
            if (LOGGER_OBJECT not in self.loggers):
                self.loggers.append(LOGGER_OBJECT)
            
        if LOGGER_PLOT in self.loggers:
            self.avgobj = DGILibAverages(self.dgilib_extra, self.plotobj.preprocessed_averages_data, *args, **kwargs)
            #self.avgobj.dgilib_extra = self.dgilib_extra
            self.calculate_averages_for_pin = self.avgobj.calculate_all_for_pin
            self.print_averages_for_pin = self.avgobj.print_all_for_pin
        else:
            raise NotImplementedError("Need to make DGILibAverages work by itself when the plot does not precalculate data")

    def start(self):
        """Call to start logging."""
        if LOGGER_CSV in self.loggers:
            for interface in self.dgilib_extra.interfaces.values():
                interface.init_csv_writer(self.log_folder)

        if LOGGER_PLOT in self.loggers:
            pass  # TODO

        # Start the data polling
        self.start_polling()

        # Create data structure self.data if LOGGER_OBJECT is enabled
        if LOGGER_OBJECT in self.loggers:
            self.dgilib_extra.empty_data()

    def update_callback(self, return_data=False):
        """Call to get new data."""
        if return_data:
            logger_data = LoggerData()
        # Get data
        for interface_id, interface in self.dgilib_extra.interfaces.items():
            # Read from the interface
            interface_data = interface.read()
            # Check if any data has arrived
            if interface_data:
                if LOGGER_CSV in self.loggers:
                    interface.csv_write_rows(interface_data)
                # Merge data into self.data if LOGGER_OBJECT is enabled
                if LOGGER_OBJECT in self.loggers:
                    self.dgilib_extra.data[interface_id] += interface_data
                # Update the plot if LOGGER_PLOT is enabled
                if LOGGER_PLOT in self.loggers:
                    if self.plotobj is not None:
                        self.plotobj.update_plot(self.dgilib_extra.data)
                    else:
                        print("Error: There's no plot!")
                if return_data:
                    logger_data[interface_id] += interface_data

        # Return the data
        if return_data:
            return logger_data

    def stop(self, return_data=False):
        """Call to stop logging."""
        # Stop the data polling
        self.stop_polling()

        # Get last data from buffer
        if LOGGER_OBJECT in self.loggers:
            self.update_callback()
        else:
            data = self.update_callback(return_data)

        # Close file handle
        if LOGGER_CSV in self.loggers:
            for interface in self.dgilib_extra.interfaces.values():
                interface.close_csv_writer()

        if LOGGER_PLOT in self.loggers:
            self.plotobj.ax.set_title("Logged Data")
            pass  # TODO

        if LOGGER_OBJECT in self.loggers:
            return self.dgilib_extra.data
        elif return_data:
            return data

    def log(self, duration=10, stop_function=None, min_duration=0.1):
        """Run the logger for the specified amount of time.

        Keyword Arguments:
            duration {int} -- Amount of time to log data (default: {10}).
            stop_function {function} -- Function that will be evaluated on the
                collected data. If it returns False the logging will be
                stopped even if the duration has not been reached (default:
                {None}).

        Returns:
            LoggerData -- Returns the logged data as a LoggerData object if
                LOGGER_OBJECT was passed to the logger.

        """
        end_time = time() + duration
        self.start()

        if LOGGER_PLOT in self.loggers:
            # So that the plot has xmax (being time) as big as duration now
            if self.plotobj is type(DGILibPlot):
                self.plotobj.xmax = duration

        if stop_function is None:
            while (time() + min_duration > end_time) and time() < end_time:
                self.update_callback()
        elif LOGGER_OBJECT in self.loggers:
            while time() < end_time:
                self.update_callback()
                if (time() + min_duration > end_time) and stop_function(self.dgilib_extra.data):
                    break
        else:
            while time() < end_time:
                if (time() + min_duration > end_time) and stop_function(self.update_callback(True)):
                    break

        self.stop()

        if LOGGER_OBJECT in self.loggers:
            return self.dgilib_extra.data

    def which_polling(self, interface_ids=None):
        """which_polling.

        Determines on which polling types need to be started or stopped based
        on the interface ids and instantiated interfaces in dgilib extra.

        Arguments:
            interface_ids {list} -- List of interface ids (default: all
                enabled interfaces)

        Returns:
            tuple -- Tuple of bool that are true when that interface type
                should be started or stopped

        """
        if interface_ids is None:
            interface_ids = self.dgilib_extra.enabled_interfaces
        polling = power = False
        for interface_id in interface_ids:
            polling |= POLLING == \
                self.dgilib_extra.interfaces[interface_id].polling_type
            power |= POWER == \
                self.dgilib_extra.interfaces[interface_id].polling_type
        return polling, power

    def start_polling(self, interface_ids=None):
        """start_polling.

        Starts polling on the specified interfaces. By default polling will be
        started for all enabled interfaces.

        Keyword Arguments:
            interface_ids {list} -- List of interface ids (default: all
                enabled interfaces)
        """
        polling, power = self.which_polling(interface_ids)
        if polling:
            self.dgilib_extra.start_polling()
        if power:
            self.dgilib_extra.auxiliary_power_start()

    def stop_polling(self, interface_ids=None):
        """stop_polling.

        Stops polling on the specified interfaces. By default polling will be
        stopped for all enabled interfaces.

        Keyword Arguments:
            interface_ids {list} -- List of interface ids (default: all
                enabled interfaces)
        """
        polling, power = self.which_polling(interface_ids)
        if polling:
            self.dgilib_extra.stop_polling()
        if power:
            self.dgilib_extra.auxiliary_power_stop()

# # Should be removed and updated every time update_callback is called
# def logger_plot_data(data, plot_pins=[True] * 4, fig=None, ax=None):
#     """TO BE REMOVED."""
#     if ax is None:
#         if fig is None:
#             fig = plt.figure(figsize=(8, 6))
#         else:
#             fig.clf()
#         ax = fig.add_subplot(1, 1, 1)
#     # plt.gcf().set_size_inches(8, 6, forward=True)
#     ax.plot(data.power.timestamps, data.power.values)
#     if data.power:
#         max_data = max(data.power.values)
#     for pin, plot_pin in enumerate(plot_pins):
#         if plot_pin:
#             ax.plot(data.gpio.timestamps, [
#                     pin_values[pin]*max_data for pin_values in data.gpio.values])
#     ax.set_xlabel('Time [s]')
#     ax.set_ylabel('Current [A]')
#     # ax.set_title(
#     #     f"Average current: {calculate_average(data[INTERFACE_POWER])*1e3:.4}"
#     #     f" mA, with pin 2 high: "
#     #     f"{calculate_average(power_filter_by_pin(2, data))*1e3:.4} mA, with "
#     #     f"pin 3 high: "
#     #     f"{calculate_average(power_filter_by_pin(3, data))*1e3:.4}")
#     # ax.set_title(
#     #     f"Average current: {calculate_average(data[INTERFACE_POWER].get_as_lists())*1e3:.4} "
#     #     f"mA, with pin 2 high: {calculate_average_by_pin(data, 2)*1e3:.4} mA, "
#     #     f"with pin 3 high: {calculate_average_by_pin(data, 3)*1e3:.4}")
#     fig.suptitle("Logged Data")
#     fig.show()

#     while fig.fignum_exists(fig.number):
#         fig.pause(1)

#     return fig, ax
