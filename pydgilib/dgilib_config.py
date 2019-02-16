GET_STRING_SIZE = 100
NUM_INTERFACES = 10
NUM_CONFIG_IDS = 255
NUM_CALIBRATION = 255
BUFFER_SIZE = 10000000
MAX_PRINT = 100

# Interface types
INTERFACE_TIMESTAMP  = 0x00 #   0 Service interface which appends timestamps to all received events on associated interfaces.
INTERFACE_SPI        = 0x20 #  32 Communicates directly over SPI in Slave mode.
INTERFACE_USART      = 0x21 #  33 Communicates directly over USART in Slave mode.
INTERFACE_I2C        = 0x22 #  34 Communicates directly over I2C in Slave mode.
INTERFACE_GPIO       = 0x30 #  48 Monitors and controls the state of GPIO pins.
INTERFACE_POWER_DATA = 0x40 #  64 Receives data from the attached power measurement co-processors.
INTERFACE_POWER_SYNC = 0x41 #  65 Receives sync events from the attached power measurement co-processors.
INTERFACE_RESERVED   = 0xFF # 255 Special identifier used to indicate no interface.

# Circuit types
OLD_XAM = 0x00 #   0
XAM     = 0x10 #  16
PAM     = 0x11 #  17
UNKNOWN = 0xFF # 255

# Return codes
IDLE               = 0x00 #   0
RUNNING            = 0x01 #   1
DONE               = 0x02 #   2
CALIBRATING        = 0x03 #   3
INIT_FAILED        = 0x10 #  16
OVERFLOWED         = 0x11 #  17
USB_DISCONNECTED   = 0x12 #  18
CALIBRATION_FAILED = 0x20 #  32

# Power channels
CHANNEL_A = 0
CHANNEL_B = 1

# Power types
POWER_CURRENT = 0
POWER_VOLTAGE = 1
POWER_RANGE = 2