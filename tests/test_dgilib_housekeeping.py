"""This module holds the automated tests for DGILib Housekeeping."""

from pydgilib.dgilib import DGILib

from ctypes import c_uint


def test_connect():
    """test_connect.

    DGILibHousekeeping.connect
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    dgilib.dgi_hndl = dgilib.connect(device_sn)
    assert isinstance(dgilib.dgi_hndl, c_uint)
    # Test bigger than 0? Bigger than 4096
    dgilib.disconnect()


def test_disconnect():
    """test_disconnect.

    DGILibHousekeeping.disconnect
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    dgilib.dgi_hndl = dgilib.connect(device_sn)
    assert dgilib.disconnect() is None


def test_connection_status():
    """test_connection_status.

    DGILibHousekeeping.connection_status
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    assert dgilib.connection_status() == 2
    dgilib.dgi_hndl = dgilib.connect(device_sn)
    assert dgilib.connection_status() == 0
    dgilib.disconnect()
    assert dgilib.connection_status() == 2


def test_get_major_version():
    """test_get_major_version.

    DGILibHousekeeping.get_major_version
    """
    assert isinstance(DGILib().get_major_version(), int)


def test_get_minor_version():
    """test_get_minor_version.

    DGILibHousekeeping.get_minor_version
    """
    assert isinstance(DGILib().get_minor_version(), int)


def test_get_build_number():
    """test_get_build_number.

    DGILibHousekeeping.get_build_number
    """
    assert isinstance(DGILib().get_build_number(), int)


def test_get_fw_version():
    """test_get_fw_version.

    DGILibHousekeeping.get_fw_version
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    dgilib.dgi_hndl = dgilib.connect(device_sn)
    fw_version = dgilib.get_fw_version()
    assert isinstance(fw_version, tuple)
    assert len(fw_version) == 2
    assert isinstance(fw_version[0], int)
    assert isinstance(fw_version[1], int)
    dgilib.disconnect()


def test_start_polling():
    """test_start_polling.

    DGILibHousekeeping.start_polling
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    dgilib.dgi_hndl = dgilib.connect(device_sn)
    assert dgilib.start_polling() is None
    # assert dgilib.start_polling() is None
    # dgilib.stop_polling()  # All tests seems to pass without this as well
    dgilib.disconnect()
    # NOTE: Calling start_polling() twice in a row  and not calling
    # disconnect afterwards resulted in mode 17


def test_stop_polling():
    """test_stop_polling.

    DGILibHousekeeping.stop_polling
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    dgilib.dgi_hndl = dgilib.connect(device_sn)
    assert dgilib.stop_polling() is None
    assert dgilib.stop_polling() is None
    dgilib.start_polling()
    assert dgilib.stop_polling() is None
    dgilib.disconnect()


def test_target_reset():
    """test_target_reset.

    DGILibHousekeeping.target_reset
    """
    dgilib = DGILib()
    dgilib.discover()
    device_sn = dgilib.get_device_serial()
    dgilib.dgi_hndl = dgilib.connect(device_sn)
    assert dgilib.target_reset(False) is None
    assert dgilib.target_reset(False) is None
    assert dgilib.target_reset(True) is None
    assert dgilib.target_reset(True) is None
    assert dgilib.target_reset(False) is None
    dgilib.disconnect()
