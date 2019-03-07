"""This module holds the automated tests for DGILib Interface Communication."""

from pydgilib.dgilib import DGILib
from pydgilib.dgilib_config import (
    NUM_INTERFACES, INTERFACE_TIMESTAMP, INTERFACE_SPI, INTERFACE_USART,
    INTERFACE_I2C, INTERFACE_GPIO, INTERFACE_POWER_DATA, INTERFACE_POWER_SYNC,
    INTERFACE_RESERVED)

from time import sleep
import unittest


class TestDGILibInterfaceCommunication(unittest.TestCase):
    """Tests for DGILib Interface Communication."""

    polling_duration = 1  # Number of seconds to log data for in read and clear tests

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

    def test_interface_list(self):
        """test_interface_list."""
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            self.assertIsInstance(interfaces, list)
            self.assertLess(len(interfaces), NUM_INTERFACES)
            for interface in interfaces:
                self.assertIn(interface, self.INTERFACES)

    def test_interface_enable(self):
        """test_interface_enable."""
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_ENABLE:
                if interface_id in interfaces:
                    self.assertIsNone(dgilib.interface_enable(interface_id))

    def test_interface_disable(self):
        """test_interface_disable."""
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES:
                if interface_id in interfaces:
                    self.assertIsNone(dgilib.interface_disable(interface_id))

    def test_interface_get_configuration(self):
        """test_interface_get_configuration."""
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES:
                if interface_id in interfaces:
                    config = dgilib.interface_get_configuration(interface_id)
                    self.assertIsInstance(config, tuple)
                    self.assertEqual(len(config), 2)
                    self.assertIsInstance(config[0], list)
                    self.assertIsInstance(config[1], list)

    def test_interface_set_configuration(self):
        """test_interface_set_configuration.

        Gets the configuration and sets it to the same values.
        """
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_SET_CONFIG:
                if interface_id in interfaces:
                    config = dgilib.interface_get_configuration(interface_id)
                    self.assertIsNone(
                        dgilib.interface_set_configuration(interface_id, *config))

    def test_interface_clear_buffer(self):
        """test_interface_clear_buffer."""
        # When not enabled
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES:
                if interface_id in interfaces:
                    self.assertIsNone(
                        dgilib.interface_clear_buffer(interface_id))
        # When enabled
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_ENABLE:
                if interface_id in interfaces:
                    dgilib.interface_enable(interface_id)
                    self.assertIsNone(
                        dgilib.interface_clear_buffer(interface_id))
                    dgilib.interface_disable(interface_id)
        # When enabled and polling
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_ENABLE:
                if interface_id in interfaces:
                    dgilib.interface_enable(interface_id)
                    dgilib.start_polling()
                    sleep(self.polling_duration)
                    self.assertIsNone(
                        dgilib.interface_clear_buffer(interface_id))
                    dgilib.stop_polling()
                    dgilib.interface_disable(interface_id)

    def test_interface_read_data(self):
        """test_interface_read_data."""
        # When not enabled
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_ENABLE:
                if interface_id in interfaces:
                    data = dgilib.interface_read_data(interface_id)
                    self.assertIsInstance(data, tuple)
                    self.assertEqual(len(data), 2)
                    self.assertIsInstance(data[0], list)
                    self.assertIsInstance(data[1], list)
                    self.assertEqual(len(data[0]), len(data[1]))
        # When enabled
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_ENABLE:
                if interface_id in interfaces:
                    dgilib.interface_enable(interface_id)
                    data = dgilib.interface_read_data(interface_id)
                    self.assertIsInstance(data, tuple)
                    self.assertEqual(len(data), 2)
                    self.assertIsInstance(data[0], list)
                    self.assertIsInstance(data[1], list)
                    self.assertEqual(len(data[0]), len(data[1]))
                    dgilib.interface_disable(interface_id)
        # When enabled and polling
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_ENABLE:
                if interface_id in interfaces:
                    dgilib.interface_enable(interface_id)
                    dgilib.start_polling()
                    sleep(self.polling_duration)
                    data = dgilib.interface_read_data(interface_id)
                    self.assertIsInstance(data, tuple)
                    self.assertEqual(len(data), 2)
                    self.assertIsInstance(data[0], list)
                    self.assertIsInstance(data[1], list)
                    self.assertEqual(len(data[0]), len(data[1]))
                    dgilib.stop_polling()
                    dgilib.interface_disable(interface_id)

    def test_interface_write_data(self):
        """test_interface_write_data."""
        # When not enabled
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_WRITE:
                if interface_id in interfaces:
                    self.assertIsNone(
                        dgilib.interface_write_data(interface_id, [0]))
        # When enabled
        with DGILib() as dgilib:
            interfaces = dgilib.interface_list()
            for interface_id in self.INTERFACES_WRITE:
                if interface_id in interfaces:
                    dgilib.interface_enable(interface_id)
                    self.assertIsNone(
                        dgilib.interface_write_data(interface_id, [0]))
                    dgilib.interface_disable(interface_id)
