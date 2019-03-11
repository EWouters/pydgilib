import matplotlib.pyplot as plt
from pydgilib_extra import *
import matplotlib
matplotlib.use('WXAgg')
plt.ion()
fig = plt.figure(figsize=(8, 6))
fig.show()
data = []

# config_dict = {
#     "dgilib_path": dgilib_path,
#     "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
#     "power_buffers": [{"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
#     "read_mode": [True, True, True, True],
#     "write_mode": [False, False, False, False],
#     "loggers": [LOGGER_OBJECT, LOGGER_CSV],
#     #     "plot_pins": [False, False, True, True],
#     "plot_pins": [False, False, False, False],
#     "gpio_delay_time": 0.010795,
#     # "fig": fig,
#     "verbose": 0,
# }

# # fig.clf()

# with DGILibExtra(**config_dict) as dgilib:
#     dgilib.device_reset()
#     # data = dgilib.logger.update_callback()
#     data = dgilib.logger.log(1)

# print(data)

data_obj = []

config_dict = {
    "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
    "power_buffers": [{"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
    "read_mode": [True, True, True, True],
    "loggers": [LOGGER_OBJECT, LOGGER_PLOT, LOGGER_CSV],
    "plot_pins": [False, False, True, True],
    "plot_pins_values": [True, True, True, True],
    "gpio_delay_time": 0.0007,
    "plot_pins_method": "line",
    "plot_xmax": 15,
    "fig": fig,
    "window_title": "Experiment",
    "file_name_base": "experiment"
}

with DGILibExtra(**config_dict) as dgilib:
    dgilib.device_reset()
    data = dgilib.logger.log(15)
    data_obj = dgilib.data

fig.show()

print(data)
print(data_obj)
