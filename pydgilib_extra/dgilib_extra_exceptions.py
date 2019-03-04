"""Custom Exceptions for DGILibExtra."""

from pydgilib.dgilib_exceptions import Error


class PowerStatusError(Error):
    """Exception raised when checking `auxiliary_power_get_status()`."""

    pass


class PowerReadError(Error):
    """Exception raised when reading power buffer."""

    pass
