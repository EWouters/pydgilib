"""This module holds the automated tests for DGILib."""

from pydgilib_extra.dgilib_extra_config import NUM_PINS
from pydgilib_extra.dgilib_interface_gpio import (int2bool, bool2int)

import pytest


@pytest.mark.parametrize("i", range(2**NUM_PINS))
def test_int2bool2int(i):
    """test_int2bool2int."""
    assert i == bool2int(int2bool(i))
