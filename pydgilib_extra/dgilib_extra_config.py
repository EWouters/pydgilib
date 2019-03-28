"""Configuration for PyDGILibExtra."""

from pydgilib.dgilib_config import (
    INTERFACE_SPI, INTERFACE_USART, INTERFACE_I2C, INTERFACE_GPIO)

# Logger types
LOGGER_CSV = 0
LOGGER_OBJECT = 1
LOGGER_PLOT = 2

INTERFACE_POWER = 0x100  # 256

NUM_PINS = 4

FILE_NAME_BASE = "log"

INTERFACES = {
    "spi": INTERFACE_SPI,
    "usart": INTERFACE_USART,
    "i2c": INTERFACE_I2C,
    "gpio": INTERFACE_GPIO,
    "power": INTERFACE_POWER}

POLLING = 0
POWER = 1
