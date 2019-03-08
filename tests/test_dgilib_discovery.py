"""This module holds the automated tests for DGILib Discovery."""

from pydgilib.dgilib import DGILib
from pydgilib.dgilib_exceptions import DeviceReturnError
import unittest
import pytest


class TestDGILibDiscovery(unittest.TestCase):
    """Tests for DGILib Discovery."""

    def test_discover(self):
        """test_discover."""
        self.assertIsNone(DGILib().discover())

    def test_get_device_count(self):
        """test_get_device_count."""
        dgilib = DGILib()
        dgilib.discover()
        self.assertIsInstance(dgilib.get_device_count(), int)

    def test_get_device_name(self):
        """test_get_device_name."""
        dgilib = DGILib()
        dgilib.discover()
        self.assertIsInstance(dgilib.get_device_name(), bytes)

    def test_get_device_serial(self):
        """test_get_device_serial."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        self.assertIsInstance(device_sn, bytes)
        self.assertEqual(len(device_sn), 20)

    def test_is_msd_mode(self):
        """test_is_msd_mode."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        self.assertFalse(dgilib.is_msd_mode(device_sn))

    @pytest.mark.xfail(raises=DeviceReturnError, reason="It seems this is " +
                       "not supported by my test setup.")
    @pytest.mark.xfail(raises=OSError, reason="Using older version of dgilib." +
                       "dll")
    def test_set_mode(self):
        """test_set_mode."""
        dgilib = DGILib()
        dgilib.discover()
        device_sn = dgilib.get_device_serial()
        dgilib.set_mode(device_sn, 0)
        self.assertTrue(dgilib.is_msd_mode(device_sn))
        dgilib.set_mode(device_sn)
        self.assertFalse(dgilib.is_msd_mode(device_sn))
