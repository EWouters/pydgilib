"""This module holds the automated tests for DGILib Auxiliary."""

from pydgilib.dgilib import DGILib
from pydgilib.dgilib_config import (
    CHANNEL_A, CHANNEL_B, POWER_CURRENT, POWER_VOLTAGE, POWER_RANGE)

from time import sleep
import unittest
import pytest
from parameterized import parameterized
from ctypes import c_uint


class TestDGILibAuxiliary(unittest.TestCase):
    """Tests for DGILib Auxiliary."""

    def test_auxiliary_power_initialize(self):
        """test_auxiliary_power_initialize."""
        with DGILib() as dgilib:
            self.assertIsInstance(dgilib.auxiliary_power_initialize(), c_uint)

    def test_auxiliary_power_uninitialize(self):
        """test_auxiliary_power_uninitialize."""
        with DGILib() as dgilib:
            dgilib.auxiliary_power_initialize()
            sleep(2)  # No idea why this test fails, it is used in dgilib_extra
            self.assertIsNone(dgilib.auxiliary_power_uninitialize())


# auxiliary_power_register_buffer_pointers = DGILibAuxiliary.auxiliary_power_register_buffer_pointers
    @parameterized.expand([
        (CHANNEL_A, POWER_CURRENT), (CHANNEL_B, POWER_CURRENT),
        (CHANNEL_A, POWER_VOLTAGE), (CHANNEL_B, POWER_VOLTAGE),
        (CHANNEL_A, POWER_RANGE), (CHANNEL_B, POWER_RANGE)])
    def test_auxiliary_power_register_buffer_pointers(self, channel, power_type):
        """test_auxiliary_power_register_buffer_pointers."""
        with DGILib() as dgilib:
            dgilib.auxiliary_power_initialize()
            dgilib.auxiliary_power_register_buffer_pointers(
                channel, power_type)
            dgilib.auxiliary_power_unregister_buffer_pointers(
                channel, power_type)
            dgilib.auxiliary_power_uninitialize()

# auxiliary_power_unregister_buffer_pointers = DGILibAuxiliary.auxiliary_power_unregister_buffer_pointers
# auxiliary_power_calibration_is_valid = DGILibAuxiliary.auxiliary_power_calibration_is_valid
# auxiliary_power_trigger_calibration = DGILibAuxiliary.auxiliary_power_trigger_calibration
# auxiliary_power_get_calibration = DGILibAuxiliary.auxiliary_power_get_calibration
# auxiliary_power_get_circuit_type = DGILibAuxiliary.auxiliary_power_get_circuit_type
# auxiliary_power_get_status = DGILibAuxiliary.auxiliary_power_get_status
# auxiliary_power_start = DGILibAuxiliary.auxiliary_power_start
# auxiliary_power_stop = DGILibAuxiliary.auxiliary_power_stop
# auxiliary_power_lock_data_for_reading = DGILibAuxiliary.auxiliary_power_lock_data_for_reading
# auxiliary_power_copy_data = DGILibAuxiliary.auxiliary_power_copy_data
# auxiliary_power_free_data = DGILibAuxiliary.auxiliary_power_free_data
