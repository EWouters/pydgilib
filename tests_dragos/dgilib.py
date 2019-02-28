from pydgilib_extra import *

import numpy as np
import queue

config_dict = {
    "power_buffers": [{"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
    "read_mode": [True, True, True, True],
    "write_mode": [False, False, False, False],
    "loggers": [LOGGER_PLOT],
    "verbose": 0,
    "plot_xmax": 10,
    "plot_ymax": 0.0040,
    "plot_pins": [False, False, True, True]
}

# import pydgilib_extra.dgilib_logger
# print(pydgilib_extra.dgilib_logger)
# print(pydgilib_extra.dgilib_logger.__file__)

with DGILibExtra(**config_dict) as dgilib:
    data = dgilib.logger(10)

    dgilib.hold_plot()
