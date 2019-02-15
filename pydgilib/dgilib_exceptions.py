# Custom Exceptions
class Error(Exception):
    """Base class for exceptions in this module.
    :param msg: Error message associated with the exception
    :type msg: str
    :ivar msg: Error message associated with the exception
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class DLLError(Error):
    """Exception raised opening dgilib.dll. dgilib.dll could not be found in the specicied path"""

    pass


class DeviceIndexError(Error):
    """Exception raised selecting device: the device_index exeeds the device_count"""

    pass


class DeviceReturnError(Error):
    """Exception raised: DGILib returned non-zero value"""

    pass


class DeviceConnectionError(Error):
    """Exception raised: Could not connect to the device"""

    pass


class DeviceArgumentError(Error):
    """Exception raised parsing arguments"""

    pass

