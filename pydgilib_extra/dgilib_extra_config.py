from pydgilib.dgilib_config import *

# Logger types
LOGGER_CSV = 0
LOGGER_OBJECT = 1
LOGGER_PLOT = 2

INTERFACE_POWER = 0x100  # 256

LOGGER_CSV_HEADER = {
    INTERFACE_GPIO: ["timestamp", "gpio0", "gpio1", "gpio2", "gpio3"],
    INTERFACE_POWER: {
        POWER_CURRENT: ["timestamp", "curent"],
        POWER_VOLTAGE: ["timestamp", "voltage"],
        POWER_RANGE: ["timestamp", "range"],
    },
}