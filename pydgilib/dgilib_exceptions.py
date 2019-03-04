"""Custom Exceptions for DGILib."""


class Error(Exception):
    """Base class for exceptions in this module.

    :param msg: Error message associated with the exception
    :type msg: str
    :ivar msg: Error message associated with the exception
    """

    def __init__(self, msg):
        """__init__."""
        self.msg = msg

    def __str__(self):
        """__str__."""
        return self.msg


class DLLError(Error):
    """Exception raised opening dgilib.dll.

    dgilib.dll could not be found in the specified path.
    """

    pass


class DeviceIndexError(Error):
    """Exception raised selecting device.

    The device_index exceeds the device_count.
    """

    pass


class DeviceReturnError(Error):
    """Exception raised: DGILib returned non-zero value."""

    pass


class DeviceConnectionError(Error):
    """Exception raised: Could not connect to the device."""

    pass


class DeviceArgumentError(Error):
    """Exception raised parsing arguments."""

    pass
