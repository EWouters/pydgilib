"""This module holds the automated tests for DGILib Interface Communication."""

from pydgilib.dgilib import DGILib
from pydgilib.dgilib_config import (
    NUM_INTERFACES, INTERFACE_TIMESTAMP, INTERFACE_SPI, INTERFACE_USART,
    INTERFACE_I2C, INTERFACE_GPIO, INTERFACE_POWER_DATA, INTERFACE_POWER_SYNC,
    INTERFACE_RESERVED)

from time import sleep

import pytest

verbosity = (0, 99)

# Number of seconds to log data for in read and clear tests
polling_duration = 1

INTERFACES = [INTERFACE_TIMESTAMP,
              INTERFACE_SPI,
              INTERFACE_USART,
              INTERFACE_I2C,
              INTERFACE_GPIO,
              INTERFACE_POWER_DATA,
              INTERFACE_POWER_SYNC,
              80,  # Not in documentation
              INTERFACE_RESERVED]

INTERFACES_ENABLE = [INTERFACE_SPI,
                     INTERFACE_USART,
                     INTERFACE_I2C,
                     INTERFACE_GPIO,
                     INTERFACE_POWER_SYNC,
                     80,  # Not in documentation
                     INTERFACE_RESERVED]

INTERFACES_SET_CONFIG = [INTERFACE_TIMESTAMP,
                         INTERFACE_SPI,
                         INTERFACE_USART,
                         INTERFACE_I2C,
                         INTERFACE_GPIO,
                         INTERFACE_POWER_SYNC,
                         80,  # Not in documentation
                         INTERFACE_RESERVED]

INTERFACES_WRITE = [INTERFACE_USART,
                    INTERFACE_I2C,
                    INTERFACE_GPIO,
                    INTERFACE_RESERVED]


@pytest.mark.parametrize("verbose", verbosity)
def test_interface_list(verbose):
    """test_interface_list.

    DGILibInterfaceCommunication.interface_list
    """
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        assert isinstance(interfaces, list)
        assert len(interfaces) < NUM_INTERFACES
        for interface in interfaces:
            assert interface in INTERFACES


@pytest.mark.parametrize("verbose", verbosity)
def test_interface_enable(verbose):
    """test_interface_enable.

    DGILibInterfaceCommunication.interface_enable
    """
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_ENABLE:
            if interface_id in interfaces:
                assert dgilib.interface_enable(interface_id) is None


@pytest.mark.parametrize("verbose", verbosity)
def test_interface_disable(verbose):
    """test_interface_disable.

    DGILibInterfaceCommunication.interface_disable
    """
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES:
            if interface_id in interfaces:
                assert dgilib.interface_disable(interface_id) is None


@pytest.mark.parametrize("verbose", verbosity)
def test_interface_get_configuration(verbose):
    """test_interface_get_configuration.

    DGILibInterfaceCommunication.interface_get_configuration
    """
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES:
            if interface_id in interfaces:
                config = dgilib.interface_get_configuration(interface_id)
                assert isinstance(config, tuple)
                assert len(config) == 2
                assert isinstance(config[0], list)
                assert isinstance(config[1], list)


@pytest.mark.parametrize("verbose", verbosity)
def test_interface_set_configuration(verbose):
    """test_interface_set_configuration.

    DGILibInterfaceCommunication.interface_set_configuration

    Gets the configuration and sets it to the same values.
    """
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_SET_CONFIG:
            if interface_id in interfaces:
                config = dgilib.interface_get_configuration(interface_id)
                assert dgilib.interface_set_configuration(
                    interface_id, *config) is None


@pytest.mark.parametrize("verbose", verbosity)
def test_interface_clear_buffer(verbose):
    """test_interface_clear_buffer.

    DGILibInterfaceCommunication.interface_clear_buffer
    """
    # When not enabled
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES:
            if interface_id in interfaces:
                assert dgilib.interface_clear_buffer(interface_id) is None
    # When enabled
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_ENABLE:
            if interface_id in interfaces:
                dgilib.interface_enable(interface_id)
                assert dgilib.interface_clear_buffer(interface_id) is None
                dgilib.interface_disable(interface_id)
    # When enabled and polling
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_ENABLE:
            if interface_id in interfaces:
                dgilib.interface_enable(interface_id)
                dgilib.start_polling()
                sleep(polling_duration)
                assert dgilib.interface_clear_buffer(interface_id) is None
                dgilib.stop_polling()
                dgilib.interface_disable(interface_id)


@pytest.mark.parametrize("verbose", verbosity)
def test_interface_read_data(verbose):
    """test_interface_read_data.

    DGILibInterfaceCommunication.interface_read_data
    """
    # When not enabled
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_ENABLE:
            if interface_id in interfaces:
                data = dgilib.interface_read_data(interface_id)
                assert isinstance(data, tuple)
                assert len(data) == 2
                assert isinstance(data[0], list)
                assert isinstance(data[1], list)
                assert len(data[0]) == len(data[1])
    # When enabled
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_ENABLE:
            if interface_id in interfaces:
                dgilib.interface_enable(interface_id)
                data = dgilib.interface_read_data(interface_id)
                assert isinstance(data, tuple)
                assert len(data) == 2
                assert isinstance(data[0], list)
                assert isinstance(data[1], list)
                assert len(data[0]) == len(data[1])
                dgilib.interface_disable(interface_id)
    # When enabled and polling
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_ENABLE:
            if interface_id in interfaces:
                dgilib.interface_enable(interface_id)
                dgilib.start_polling()
                sleep(polling_duration)
                data = dgilib.interface_read_data(interface_id)
                assert isinstance(data, tuple)
                assert len(data) == 2
                assert isinstance(data[0], list)
                assert isinstance(data[1], list)
                assert len(data[0]) == len(data[1])
                dgilib.stop_polling()
                dgilib.interface_disable(interface_id)


@pytest.mark.parametrize("verbose", verbosity)
def test_interface_write_data(verbose):
    """test_interface_write_data.

    DGILibInterfaceCommunication.interface_write_data
    """
    # When not enabled
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_WRITE:
            if interface_id in interfaces:
                assert dgilib.interface_write_data(interface_id, [0]) is None
    # When enabled
    with DGILib(verbose=verbose) as dgilib:
        interfaces = dgilib.interface_list()
        for interface_id in INTERFACES_WRITE:
            if interface_id in interfaces:
                dgilib.interface_enable(interface_id)
                assert dgilib.interface_write_data(interface_id, [0]) is None
                dgilib.interface_disable(interface_id)
