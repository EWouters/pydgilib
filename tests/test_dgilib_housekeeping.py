"""This module holds the automated tests for DGILib Housekeeping."""

from pydgilib.dgilib import DGILib
import unittest

from ctypes import c_uint


class TestDGILibHousekeeping(unittest.TestCase):
    """Tests for DGILib Housekeeping."""

    def test_connect(self):
        """test_connect."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        dgilib.dgi_hndl = dgilib.connect(device_sn)
        self.assertIsInstance(dgilib.dgi_hndl, c_uint)
        # Test bigger than 0? Bigger than 4096
        dgilib.disconnect()

    def test_disconnect(self):
        """test_disconnect."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        dgilib.dgi_hndl = dgilib.connect(device_sn)
        self.assertIsNone(dgilib.disconnect())

    def test_connection_status(self):
        """test_connection_status."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        self.assertEqual(dgilib.connection_status(), 2)
        dgilib.dgi_hndl = dgilib.connect(device_sn)
        self.assertEqual(dgilib.connection_status(), 0)
        dgilib.disconnect()
        self.assertEqual(dgilib.connection_status(), 2)

    def test_get_major_version(self):
        """test_get_major_version."""
        self.assertIsInstance(DGILib().get_major_version(), int)

    def test_get_minor_version(self):
        """test_get_minor_version."""
        self.assertIsInstance(DGILib().get_minor_version(), int)

    def test_get_build_number(self):
        """test_get_build_number."""
        self.assertIsInstance(DGILib().get_build_number(), int)

    def test_get_fw_version(self):
        """test_get_fw_version."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        dgilib.dgi_hndl = dgilib.connect(device_sn)
        fw_version = dgilib.get_fw_version()
        self.assertIsInstance(fw_version, tuple)
        self.assertEqual(len(fw_version), 2)
        self.assertIsInstance(fw_version[0], int)
        self.assertIsInstance(fw_version[1], int)
        dgilib.disconnect()

    def test_start_polling(self):
        """test_start_polling."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        dgilib.dgi_hndl = dgilib.connect(device_sn)
        self.assertIsNone(dgilib.start_polling())
        # self.assertIsNone(dgilib.start_polling())
        # dgilib.stop_polling()  # All tests seems to pass without this as well
        dgilib.disconnect()
        # NOTE: Calling start_polling() twice in a row  and not calling
        # disconnect afterwards resulted in mode 17

    def test_stop_polling(self):
        """test_stop_polling."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        dgilib.dgi_hndl = dgilib.connect(device_sn)
        self.assertIsNone(dgilib.stop_polling())
        self.assertIsNone(dgilib.stop_polling())
        dgilib.start_polling()
        self.assertIsNone(dgilib.stop_polling())
        dgilib.disconnect()

    def test_target_reset(self):
        """test_target_reset."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        dgilib.dgi_hndl = dgilib.connect(device_sn)
        self.assertIsNone(dgilib.target_reset(False))
        self.assertIsNone(dgilib.target_reset(False))
        self.assertIsNone(dgilib.target_reset(True))
        self.assertIsNone(dgilib.target_reset(True))
        self.assertIsNone(dgilib.target_reset(False))
        dgilib.disconnect()
