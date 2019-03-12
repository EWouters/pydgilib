"""This module holds the automated tests for DGILib Auxiliary."""

from pydgilib.dgilib import DGILib
from pydgilib.dgilib_config import (
    CHANNEL_A, CHANNEL_B, POWER_CURRENT, POWER_VOLTAGE, POWER_RANGE, OLD_XAM,
    XAM, PAM, UNKNOWN, NUM_CALIBRATION, IDLE, RUNNING, DONE, CALIBRATING,
    INIT_FAILED, OVERFLOWED, USB_DISCONNECTED, CALIBRATION_FAILED, BUFFER_SIZE)

import pytest
from ctypes import c_uint


def test_auxiliary_power_initialize():
    """test_auxiliary_power_initialize.

    DGILibAuxiliary.auxiliary_power_initialize
    """
    with DGILib() as dgilib:
        assert isinstance(dgilib.auxiliary_power_initialize(), c_uint)


def test_auxiliary_power_uninitialize():
    """test_auxiliary_power_uninitialize.

    DGILibAuxiliary.auxiliary_power_uninitialize
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        assert dgilib.auxiliary_power_uninitialize() is None


@pytest.mark.parametrize("channel, power_type", [
    (CHANNEL_A, POWER_CURRENT), (CHANNEL_B, POWER_CURRENT),
    (CHANNEL_A, POWER_VOLTAGE), (CHANNEL_B, POWER_VOLTAGE),
    (CHANNEL_A, POWER_RANGE), (CHANNEL_B, POWER_RANGE)])
def test_auxiliary_power_register_unregister_buffer_pointers(channel,
                                                             power_type):
    """test_auxiliary_power_register_unregister_buffer_pointers.

    DGILibAuxiliary.auxiliary_power_register_buffer_pointers
    DGILibAuxiliary.auxiliary_power_unregister_buffer_pointers
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        dgilib.auxiliary_power_register_buffer_pointers(
            channel, power_type)
        dgilib.auxiliary_power_unregister_buffer_pointers(
            channel, power_type)
        dgilib.auxiliary_power_uninitialize()


def test_auxiliary_power_calibration_is_valid():
    """test_auxiliary_power_calibration_is_valid.

    DGILibAuxiliary.auxiliary_power_calibration_is_valid
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        assert isinstance(dgilib.auxiliary_power_calibration_is_valid(), bool)
        dgilib.auxiliary_power_uninitialize()


def test_auxiliary_power_get_circuit_type():
    """test_auxiliary_power_get_circuit_type.

    DGILibAuxiliary.auxiliary_power_get_circuit_type
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        assert dgilib.auxiliary_power_get_circuit_type() in (OLD_XAM, XAM, PAM,
                                                             UNKNOWN)
        dgilib.auxiliary_power_uninitialize()


def test_auxiliary_power_trigger_calibration():
    """test_auxiliary_power_trigger_calibration.

    DGILibAuxiliary.auxiliary_power_trigger_calibration
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        assert dgilib.auxiliary_power_trigger_calibration(
            dgilib.auxiliary_power_get_circuit_type()) is None
        dgilib.auxiliary_power_uninitialize()


def test_auxiliary_power_get_calibration():
    """test_auxiliary_power_get_calibration.

    DGILibAuxiliary.auxiliary_power_get_calibration
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        calibration_data = dgilib.auxiliary_power_get_calibration()
        assert len(calibration_data) < NUM_CALIBRATION
        assert isinstance(calibration_data, list)
        dgilib.auxiliary_power_uninitialize()


def test_auxiliary_power_get_status():
    """test_auxiliary_power_get_status.

    DGILibAuxiliary.auxiliary_power_get_status
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        assert dgilib.auxiliary_power_get_status() in (
            IDLE, RUNNING, DONE, CALIBRATING, INIT_FAILED, OVERFLOWED,
            USB_DISCONNECTED, CALIBRATION_FAILED)
        dgilib.auxiliary_power_uninitialize()


@pytest.mark.parametrize("channel, power_type", [
    (CHANNEL_A, POWER_CURRENT), (CHANNEL_B, POWER_CURRENT),
    (CHANNEL_A, POWER_VOLTAGE), (CHANNEL_B, POWER_VOLTAGE),
    (CHANNEL_A, POWER_RANGE), (CHANNEL_B, POWER_RANGE)])
@pytest.mark.parametrize("mode, parameter", [(0, 0), (1, 1), ])
def test_auxiliary_power_start_stop(channel, power_type, mode, parameter):
    """test_auxiliary_power_start_stop.

    DGILibAuxiliary.auxiliary_power_start
    DGILibAuxiliary.auxiliary_power_stop
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        dgilib.auxiliary_power_register_buffer_pointers(channel, power_type)
        assert dgilib.auxiliary_power_start(
            mode=mode, parameter=parameter) is None
        assert dgilib.auxiliary_power_stop() is None
        dgilib.auxiliary_power_unregister_buffer_pointers(channel, power_type)
        dgilib.auxiliary_power_uninitialize()


@pytest.mark.parametrize("channel, power_type", [
    (CHANNEL_A, POWER_CURRENT), (CHANNEL_B, POWER_CURRENT),
    (CHANNEL_A, POWER_VOLTAGE), (CHANNEL_B, POWER_VOLTAGE),
    (CHANNEL_A, POWER_RANGE), (CHANNEL_B, POWER_RANGE)])
def test_auxiliary_power_lock_data_for_reading_copy_data_free_data(channel,
                                                                   power_type):
    """test_auxiliary_power_lock_data_for_reading_copy_data_free_data.

    DGILibAuxiliary.auxiliary_power_lock_data_for_reading
    DGILibAuxiliary.auxiliary_power_copy_data
    DGILibAuxiliary.auxiliary_power_free_data
    """
    with DGILib() as dgilib:
        dgilib.power_hndl = dgilib.auxiliary_power_initialize()
        dgilib.auxiliary_power_register_buffer_pointers(
            channel, power_type)
        dgilib.auxiliary_power_start()
        assert dgilib.auxiliary_power_lock_data_for_reading() is None
        powerTimestamp, powerBuffer = dgilib.auxiliary_power_copy_data(
            channel, power_type)
        assert len(powerTimestamp) == len(powerBuffer)
        assert len(powerTimestamp) < BUFFER_SIZE
        assert isinstance(powerTimestamp, list)
        assert isinstance(powerBuffer, list)
        assert dgilib.auxiliary_power_free_data() is None
        dgilib.auxiliary_power_stop()
        dgilib.auxiliary_power_unregister_buffer_pointers(
            channel, power_type)
        dgilib.auxiliary_power_uninitialize()
