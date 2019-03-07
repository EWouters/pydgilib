# pylint: disable=E1101
"""This module wraps the logging functionality for DGILibExtra."""

import copy
from os import curdir
from time import time

# Todo, remove dependency
# import matplotlib.pyplot as plt

from pydgilib.dgilib_config import INTERFACE_GPIO
from pydgilib_extra.dgilib_data import LoggerData
from pydgilib_extra.dgilib_extra_config import (
    INTERFACE_POWER, LOGGER_CSV, LOGGER_OBJECT, LOGGER_PLOT, FILE_NAME_BASE,
    POLLING, POWER)
# from pydgilib_extra.dgilib_interface_gpio import gpio_augment_edges
from pydgilib_extra.dgilib_plot import DGILibPlot

how_many_times = 0

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
        if LOGGER_CSV not in self.loggers and (
            "file_name_base" in kwargs or "log_folder" in kwargs
        ):
            self.loggers.append(LOGGER_CSV)

        # file_name_base - merely the optional base of the filename
        #     (Preferably leave standard).
        # log_folder - where log files will be saved
        self.file_name_base = kwargs.get("file_name_base", FILE_NAME_BASE)
        self.log_folder = kwargs.get("log_folder", curdir)

        # Enable the plot logger if figure has been specified.
        if (LOGGER_PLOT not in self.loggers and
                ("fig" in kwargs or "ax" in kwargs)):
            self.loggers.append(LOGGER_PLOT)

        # Set self.figure if LOGGER_PLOT enabled
        # Create axes self.axes if LOGGER_PLOT is enabled
        if LOGGER_PLOT in self.loggers:
            self.plotobj = DGILibPlot(self, self.dgilib_extra, *args, **kwargs)
            self.plot_pause = self.plotobj.plot_pause
            self.plot_still_exists = self.plotobj.plot_still_exists
            self.keep_plot_alive = self.plotobj.keep_plot_alive

            # Force logging in object if logging in plot
            if (LOGGER_OBJECT not in self.loggers):
                self.loggers.append(LOGGER_OBJECT)

    def start(self):
        """Call to start logging."""
        if LOGGER_CSV in self.loggers:
            for interface in self.dgilib_extra.interfaces.values():
                interface.init_csv_writer()

        if LOGGER_PLOT in self.loggers:
            pass  # TODO

        # Start the data polling
        self.start_polling()

        # Create data structure self.data if LOGGER_OBJECT is enabled
        if LOGGER_OBJECT in self.loggers:
            self.dgilib_extra.data = LoggerData(
                self.dgilib_extra.enabled_interfaces)

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
        
        data = None # TODO: Maybe delete -Dragos

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
            pass  # TODO

        if LOGGER_OBJECT in self.loggers:
            return self.dgilib_extra.data
        elif return_data:
            return data

    def log(self, duration=10, stop_function=None):
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

        if stop_function is None:
            while time() < end_time:
                self.update_callback()
        else:
            while time() < end_time:
                data = self.update_callback(True)
                if not stop_function(data):
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

    # def data_add(self, data):
    #     """TO BE REMOVED."""
    #     assert(self.data.keys() == data.keys())  # TODO create error
    #     for interface_id in data.keys():
    #         for col in range(len(self.data[interface_id])):
    #             self.data[interface_id][col].extend(data[interface_id][col])

    # def power_filter_by_pin(self, pin=0, data=None):
    #     """Filter the data to when a specified pin is high."""
    #     if data is None:
    #         data = self.data

    #     return power_filter_by_pin(pin, data, self.dgilib_extra.verbose)

    # def calculate_average(self, power_data=None, start_time=None,
    #                       end_time=None):
    #     """calculate_average.

    #     Calculate average value of the power_data using the left Riemann sum.
    #     """
    #     if power_data is None:
    #         power_data = self.data[INTERFACE_POWER]

    #     return calculate_average(power_data, start_time, end_time)

    # def pin_duty_cycle(self, pin=0, data=None):
    #     pass


# def mergeData(data1, data2):
#     """mergeData.

#     Make class for data structure? Or at least make a method to merge that
#     mutates the list instead of doing multiple copies.
#     """
#     assert(data1.keys() == data2.keys())
#     for interface_id in data1.keys():
#         for col in range(len(data1[interface_id])):
#             data1[interface_id][col].extend(data2[interface_id][col])
#     return data1


def power_filter_by_pin(pin, data, verbose=0):
    """Filter the data to when a specified pin is high."""
    power_data = copy.deepcopy(data[INTERFACE_POWER])

    pin_value = False

    power_index = 0

    if verbose:
        print(
            f"power_filter_by_pin filtering  {len(power_data[0])} power "
            f"samples.")

    for timestamp, pin_values in zip(*data[INTERFACE_GPIO]):
        while (power_index < len(power_data[0]) and
               power_data[0][power_index] < timestamp):
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
    """calculate_average_by_pin.

    NOTE: NEEDS TO BE REWRITTEN!

    Calculate average value of the data while pin is high, using the left
    Riemann sum.
    """
    if start_time is None:
        start_time = data[INTERFACE_POWER].get_as_lists()[0][0]
    if end_time is None:
        end_time = data[INTERFACE_POWER].get_as_lists()[0][-1]

    last_time = start_time

    power_sum = 0
    time_sum = 0

    power_index = 0

    for timestamp, pin_values in data[INTERFACE_GPIO]:
        while (pin_values[pin] and
               power_index < len(data[INTERFACE_POWER].get_as_lists()[0]) and
               data[INTERFACE_POWER].get_as_lists()[0][power_index] <= timestamp):
            if (data[INTERFACE_POWER].get_as_lists()[0][power_index] >= start_time and
                    data[INTERFACE_POWER].get_as_lists()[0][power_index] <= end_time):
                power_sum += data[INTERFACE_POWER].get_as_lists()[1][power_index] * \
                    (data[INTERFACE_POWER].get_as_lists()
                     [0][power_index] - last_time)
                time_sum += (data[INTERFACE_POWER].get_as_lists()
                             [0][power_index] - last_time)
            last_time = data[INTERFACE_POWER].get_as_lists()[0][power_index]
            power_index += 1

    if time_sum == 0:
        return 0
    return power_sum / time_sum


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


def power_and_time_per_pulse(data, pin, verbose=0, power_factor=1e3):
    """Calculate power and time per pulse.

    Takes the data and a pin and returns a list of power and time sums for
    each pulse of the specified pin. It stops when all pins are high.

    :param data: Data structure holding the samples.
    :type data: dict(256:list(list(float), list(float)), 48:list(list(float),
        list(list(bool))))
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
                print(
                    f"power_and_time_per_pulse done, charges: {len(charges)}, "
                    f"times: {len(times)}")
            break
        if not pin_value and pin_values[pin]:
            pin_value = True
            start_time = timestamp
            last_time = timestamp
        if pin_value and not pin_values[pin]:
            pin_value = False
            end_time = timestamp
            while (power_index < len(data[INTERFACE_POWER][0]) and
                   data[INTERFACE_POWER][0][power_index] <= end_time):
                if (data[INTERFACE_POWER][0][power_index] >= start_time):
                    power_sum += data[INTERFACE_POWER][1][power_index] * \
                        (data[INTERFACE_POWER][0][power_index] - last_time)
                    time_sum += (data[INTERFACE_POWER][0]
                                 [power_index] - last_time)
                last_time = data[INTERFACE_POWER][0][power_index]
                power_index += 1

            charges.append(power_sum*power_factor)
            times.append(time_sum)
            power_sum = 0
            time_sum = 0

    return charges, times
