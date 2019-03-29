"""This module holds the automated tests for DGILibExtra."""


from pydgilib.dgilib_config import (INTERFACE_GPIO, CHANNEL_A, POWER_CURRENT)
from pydgilib_extra.dgilib_extra_config import (
    NUM_PINS, LOGGER_CSV, LOGGER_PLOT, LOGGER_OBJECT, INTERFACE_POWER)
from pydgilib_extra.dgilib_interface_gpio import (int2bool, bool2int)
from pydgilib_extra.dgilib_extra import DGILibExtra
from pydgilib_extra.dgilib_calculations import (
    power_and_time_per_pulse, rise_and_fall_times, calculate_average)
from pydgilib_extra.dgilib_data import LoggerData

import pytest
from os import path

verbosity = (0, 99)

config_dict = {
    "loggers": [LOGGER_OBJECT, LOGGER_CSV],
}

# This dict contains many default values, they test the argument handling.
config_dict_plot = {
    "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
    "power_buffers": [{"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
    "read_mode": [False, True, True, True],
    "write_mode": [True, False, False, False],
    "loggers": [LOGGER_OBJECT, LOGGER_PLOT, LOGGER_CSV],
    "plot_pins": [True, True, True, True],
    "gpio_delay_time": 0.0007,
    "plot_pins_method": "line",
    "plot_xmax": 1,
    "window_title": "UnitTest",
    "file_name_base": "unit_test"
}


@pytest.mark.parametrize("i", range(2**NUM_PINS))
def test_int2bool2int(i):
    """test_int2bool2int."""
    assert i == bool2int(int2bool(i))


@pytest.mark.parametrize("verbose", verbosity)
def test_info(verbose):
    """test_info."""
    with DGILibExtra(verbose=verbose, **config_dict) as dgilib:
        info = dgilib.info()
        assert isinstance(info, tuple)
        assert len(info) == 5
        for i in info:
            assert isinstance(i, int)


@pytest.mark.parametrize("verbose", verbosity)
def test_device_reset(verbose):
    """test_device_reset."""
    with DGILibExtra(verbose=verbose, **config_dict) as dgilib:
        dgilib.device_reset()


@pytest.mark.parametrize("verbose", verbosity)
def test_plot_simple(verbose):
    """test_plot_simple."""
    with DGILibExtra(verbose=verbose, **config_dict_plot) as dgilib:
        dgilib.device_reset()
        dgilib.logger.log(1)


@pytest.mark.parametrize("config",
                         (config_dict, config_dict_plot, {},
                          {"loggers": [LOGGER_PLOT]}))
@pytest.mark.parametrize("verbose", verbosity)
def test_plot(config, verbose):
    """test_plot."""

    pin_mask = config.get("read_mode", [True] * 4)

    def log_stop_function(logger_data):
        return len(logger_data.gpio) and all(
            pin_value or not read_mode for pin_value, read_mode in zip(
                logger_data.gpio.values[-1], pin_mask))

    def analysis_stop_function(pin_values):
        return all(pin_value or not read_mode for pin_value, read_mode in zip(
            pin_values, pin_mask))

    logger_data = LoggerData()
    with DGILibExtra(verbose=verbose, **config) as dgilib:
        dgilib.device_reset()
        dgilib.logger.log(10, log_stop_function)

        # Get data from object
        if LOGGER_OBJECT in dgilib.logger.loggers:
            logger_data = dgilib.data
        # Get data from csv files
        elif LOGGER_CSV in dgilib.logger.loggers:
            for interface_id, interface in dgilib.interfaces.items():
                logger_data[interface_id] += interface.csv_read_file(
                    path.join(dgilib.logger.log_folder,
                              (interface.file_name_base + '_' +
                               interface.name + ".csv")))

        power_and_time = power_and_time_per_pulse(
            logger_data, 1, stop_function=analysis_stop_function)
        assert len(power_and_time[0]) == len(power_and_time[1])

        rise_and_fall = rise_and_fall_times(
            logger_data, 1, stop_function=analysis_stop_function)
        assert len(rise_and_fall[0]) == len(rise_and_fall[1])

        assert 1e-3 > abs(sum(power_and_time[1]) - sum(
            (end-start for start, end in zip(*rise_and_fall))))

        average = calculate_average(logger_data.power)

        assert average > 0 and average < 1e-2
