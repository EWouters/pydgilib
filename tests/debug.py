import matplotlib.pyplot as plt
from pydgilib_extra import *
import matplotlib
matplotlib.use('WXAgg')
plt.ion()
dgilib_path = "C:\\Users\\erikw_000\\Documents\\GitHub\\Atmel-SAML11\\Python\\dgilib.dll"
# fig = plt.figure(figsize=(8, 6))
# fig.show()
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
    "dgilib_path": dgilib_path,
    "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
    "power_buffers": [
        {"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
    "read_mode": [True, True, True, True],
    "write_mode": [False, False, False, False],
    "loggers": [LOGGER_CSV, LOGGER_OBJECT],
    "verbose": 0,
}

with DGILibExtra(**config_dict) as dgilib:
    data = dgilib.logger.log(1)
    data_obj = dgilib.data

print(data)
print(data_obj)
