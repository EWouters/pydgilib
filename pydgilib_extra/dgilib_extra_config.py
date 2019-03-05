"""Configuration for PyDGILibExtra."""

from pydgilib.dgilib_config import (
    INTERFACE_SPI, INTERFACE_USART, INTERFACE_I2C, INTERFACE_GPIO,
    POWER_CURRENT, POWER_VOLTAGE, POWER_RANGE)

# Logger types
LOGGER_CSV = 0
LOGGER_OBJECT = 1
LOGGER_PLOT = 2

INTERFACE_POWER = 0x100  # 256

NUM_PINS = 4

# LOGGER_CSV_HEADER = {
#     INTERFACE_GPIO: ["timestamp"] + [f"gpio{n}" for n in range(NUM_PINS)],
#     INTERFACE_POWER: ["timestamp", "current"]}
# INTERFACE_POWER: {
#     POWER_CURRENT: ["timestamp", "current"],
#     POWER_VOLTAGE: ["timestamp", "voltage"],
#     POWER_RANGE: ["timestamp", "range"]}}

INTERFACES = {
    "spi": INTERFACE_SPI,
    "usart": INTERFACE_USART,
    "i2c": INTERFACE_I2C,
    "gpio": INTERFACE_GPIO,
    "power": INTERFACE_POWER}
