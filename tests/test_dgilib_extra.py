"""This module holds the automated tests for DGILibExtra."""


from pydgilib.dgilib_config import (INTERFACE_GPIO, CHANNEL_A, POWER_CURRENT)
from pydgilib_extra.dgilib_extra_config import (
    NUM_PINS, LOGGER_CSV, LOGGER_PLOT, LOGGER_OBJECT, INTERFACE_POWER)
from pydgilib_extra.dgilib_interface_gpio import (int2bool, bool2int)
from pydgilib_extra.dgilib_extra import DGILibExtra

import pytest


verbosity = (0, 99)


@pytest.mark.parametrize("i", range(2**NUM_PINS))
def test_int2bool2int(i):
    """test_int2bool2int."""
    assert i == bool2int(int2bool(i))


config_dict = {
    "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
    "loggers": [LOGGER_OBJECT, LOGGER_CSV],
    "gpio_delay_time": 0.010795,
}


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


@pytest.mark.parametrize("verbose", verbosity)
def test_plot(verbose):
    """test_plot."""
    with DGILibExtra(verbose=verbose, **config_dict_plot) as dgilib:
        dgilib.device_reset()
        dgilib.logger.log(1)
