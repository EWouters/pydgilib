"""This module holds the automated tests for DGILib."""

from pydgilib_extra import (DGILibExtra, LOGGER_CSV, LOGGER_OBJECT)


def test_logger_log():
    """test_logger_log."""
    config_dict = {
        "loggers": [LOGGER_OBJECT, LOGGER_CSV],
        "gpio_delay_time": 0.010795,
    }
    with DGILibExtra(**config_dict) as dgilib:
        dgilib.device_reset()
        data = dgilib.logger.log(1)
        assert len(data.gpio)
        assert len(data.power)
