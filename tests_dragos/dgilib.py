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
    "plot_ymax": 0.01,
    "plot_pins": [2]
}

with DGILibExtra(**config_dict) as dgilib:
	data = dgilib.logger(1)

	while True: a = 2+2
