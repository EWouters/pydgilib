"""This module wraps the logging functionality for DGILibExtra."""

from os import getcwd
from time import time

from pydgilib_extra.dgilib_data import LoggerData
from pydgilib_extra.dgilib_extra_config import (
    LOGGER_CSV, LOGGER_OBJECT, LOGGER_PLOT, FILE_NAME_BASE, POLLING, POWER)
from pydgilib_extra.dgilib_plot import DGILibPlot


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
        self.loggers = kwargs.get("loggers", self.dgilib_extra.default_loggers)

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

    def start(self):
        """Call to start logging."""
        if LOGGER_CSV in self.loggers:
            for interface in self.dgilib_extra.interfaces.values():
                interface.init_csv_writer(self.log_folder)

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
                    self.plotobj.update_plot(self.dgilib_extra.data)
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

        if LOGGER_OBJECT in self.loggers:
            return self.dgilib_extra.data
        elif return_data:
            return data

    def log(self, duration=10, stop_function=None, min_duration=0.2):
        """Run the logger for the specified amount of time.

        Parameters
        ----------
        duration : int
            Amount of time to log data (default: `10`).

        stop_function : callable 
            Function that will be evaluated on the
            collected data. If it returns `True` the logging will be
            stopped even if the duration has not been reached (default:
            `None`).

        Returns
        -------
        LoggerData
            Returns the logged data as a :class:`LoggerData` object if
            `LOGGER_OBJECT` was passed to the logger.
        """
        self.start()

        if LOGGER_PLOT in self.loggers:
            # So that the plot has xmax (being time) as big as duration now
            if self.plotobj is type(DGILibPlot):
                self.plotobj.xmax = duration

        cur_time = time()
        end_time = cur_time + duration
        min_time = cur_time + min_duration

        if stop_function is None:
            while time() < end_time:
                self.update_callback()
        elif LOGGER_OBJECT in self.loggers:
            while cur_time < end_time:
                self.update_callback()
                if (cur_time > min_time) and \
                        stop_function(self.dgilib_extra.data):
                    break
                cur_time = time()
        else:
            while cur_time < end_time:
                if (cur_time > min_time) and \
                        stop_function(self.update_callback(True)):
                    break
                cur_time = time()

        self.stop()

        if LOGGER_OBJECT in self.loggers:
            return self.dgilib_extra.data

    def which_polling(self, interface_ids=None):
        """which_polling

        Determines on which polling types need to be started or stopped based
        on the interface ids and instantiated interfaces in dgilib extra.

        Parameters
        ----------
        interface_ids : list
            List of interface ids (default: all enabled interfaces)

        Returns
        -------
        tuple(bool, bool, ...)
            Tuple of bool that are `True` when that interface type
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
        """start_polling

        Starts polling on the specified interfaces. By default polling will be
        started for all enabled interfaces.

        Parameters
        ----------
        interface_ids : list(int)
            List of interface ids (default: all enabled interfaces)
        """
        polling, power = self.which_polling(interface_ids)
        if polling:
            self.dgilib_extra.start_polling()
        if power:
            self.dgilib_extra.auxiliary_power_start()

    def stop_polling(self, interface_ids=None):
        """stop_polling

        Stops polling on the specified interfaces. By default polling will be
        stopped for all enabled interfaces.

        Parameters
        ----------
        interface_ids : list(int)
            List of interface ids (default: all enabled interfaces)
        """
        polling, power = self.which_polling(interface_ids)
        if polling:
            self.dgilib_extra.stop_polling()
        if power:
            self.dgilib_extra.auxiliary_power_stop()
