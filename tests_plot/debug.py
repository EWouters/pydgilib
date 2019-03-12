from pydgilib_extra import *

import numpy as np
import queue

config_dict = {
    "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
    "power_buffers": [{"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
    "read_mode": [True, True, True, True],
    "write_mode": [False, False, False, False],
    "loggers": [LOGGER_PLOT, LOGGER_CSV, LOGGER_OBJECT],
    "verbose": 0,
    "plot_xmax": 10,
    "plot_ymax": 0.0040,
    "plot_pins": [False, False, True, False],
    "plot_pins_values": [False, False, False, False],
    "plot_pins_method": "highlight",  # or wave
    "gpio_delay_time": 0.001,
}

# import pydgilib_extra.dgilib_logger
# print(pydgilib_extra.dgilib_logger)
# print(pydgilib_extra.dgilib_logger.__file__)

with DGILibExtra(**config_dict) as dgilib:
    data = dgilib.logger.log(10)

    #dgilib.logger.plotobj.draw_pins(data)
    dgilib.logger.plotobj.calculate_averages(2, dgilib.data)
    dgilib.logger.plotobj.print_averages(2)

    dgilib.logger.keep_plot_alive()
