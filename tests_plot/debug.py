from pydgilib_extra import *
from atprogram.atprogram import *

import numpy as np
import queue

# config_dict = {
#     "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
#     "power_buffers": [{"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
#     "read_mode": [True, True, True, True],
#     "write_mode": [False, False, False, False],
#     "loggers": [LOGGER_CSV, LOGGER_OBJECT],
#     "verbose": 0,
#     "plot_xmax": 5,
#     "plot_ymax": 0.0040,
#     "plot_pins": [False, False, True, False],
#     "plot_pins_values": [False, False, False, False],
#     "plot_pins_method": "highlight",
#     "automove_method" : "latest_data",
#     "gpio_delay_time": 0.0007,
# }

config_dict = {
    "loggers": [LOGGER_CSV, LOGGER_OBJECT, LOGGER_PLOT],
    "plot_pins_method": "highlight",
    "gpio_delay_time": 0.0007,
}

config_dict_plot = {
    "loggers": [LOGGER_OBJECT],
    "plot_pins_method": "highlight"
}

# import pydgilib_extra.dgilib_logger
# print(pydgilib_extra.dgilib_logger)
# print(pydgilib_extra.dgilib_logger.__file__)

atprogram("C:\\Users\\Dragos\\Dropbox\\RISE\\Other\\LEDTest\\STDIO_Redirect_w_TrustZone", verbose=1)

# data = InterfaceData(([1, 2], [3, 4]))
# print(data[::-1])

with DGILibExtra(**config_dict) as dgilib:
    data = dgilib.logger.log(5)

    avg1 = DGILibAverages(data = dgilib.data, average_function="leftpoint")
    #avg1.calculate_averages_for_pin(1)
    #avg1.print_averages_for_pin(1)

with DGILibExtra(**config_dict_plot) as dgilib:

    logger_data = LoggerData()
    for interface_id, interface in dgilib.interfaces.items():
        logger_data[interface_id] += interface.csv_read_file(
            path.join(dgilib.logger.log_folder,
                        (interface.file_name_base + '_' +
                        interface.name + ".csv")))
    
    plot = DGILibPlot(config_dict_plot)

    plot.update_plot(logger_data)

    # dgilib.logger.calculate_averages_for_pin(2)
    # dgilib.logger.print_averages_for_pin(2)

    plot.keep_plot_alive()
