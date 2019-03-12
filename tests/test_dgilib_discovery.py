"""This module holds the automated tests for DGILib Discovery."""

from pydgilib.dgilib import DGILib
from pydgilib.dgilib_exceptions import DeviceReturnError

import pytest


def test_discover():
    """test_discover.

    DGILibDiscovery.discover
    """
    assert DGILib().discover() is None


def test_get_device_count():
    """test_get_device_count.

    DGILibDiscovery.get_device_count
    """
    dgilib = DGILib()
    dgilib.discover()
    assert isinstance(dgilib.get_device_count(), int)


def test_get_device_name():
    """test_get_device_name.

    DGILibDiscovery.get_device_name
    """
    dgilib = DGILib()
    dgilib.discover()
    assert isinstance(dgilib.get_device_name(), bytes)


def test_get_device_serial():
    """test_get_device_serial.

    DGILibDiscovery.get_device_serial
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    assert isinstance(device_sn, bytes)
    assert len(device_sn) == 20


def test_is_msd_mode():
    """test_is_msd_mode.

    DGILibDiscovery.is_msd_mode
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    assert not dgilib.is_msd_mode(device_sn)


@pytest.mark.xfail(raises=DeviceReturnError, reason="It seems this is " +
                   "not supported by my test setup.")
@pytest.mark.xfail(raises=OSError, reason="Using older version of dgilib" +
                   ".dll")
def test_set_mode():
    """test_set_mode.

    DGILibDiscovery.set_mode
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    dgilib.set_mode(device_sn, 0)
    assert dgilib.is_msd_mode(device_sn)
    dgilib.set_mode(device_sn)
    assert not dgilib.is_msd_mode(device_sn)
