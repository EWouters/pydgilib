"""This module holds the automated tests for DGILib."""

from pydgilib_extra import (
    DGILib, DGILibExtra, InterfaceData, LoggerData, valid_interface_data,
    calculate_average, gpio_augment_edges, mergeData, CHANNEL_A, POWER_CURRENT,
    LOGGER_CSV, LOGGER_OBJECT, INTERFACE_POWER, INTERFACE_SPI, INTERFACE_GPIO)
import unittest

dgilib_path = "C:\\Users\\erikw_000\\Documents\\GitHub\\Atmel-SAML11\\Python\\dgilib.dll"

# # Discovery
# discovery = DGILibDiscovery
# discover = DGILibDiscovery.discover
# get_device_count = DGILibDiscovery.get_device_count
# get_device_name = DGILibDiscovery.get_device_name
# get_device_serial = DGILibDiscovery.get_device_serial
# is_msd_mode = DGILibDiscovery.is_msd_mode
# set_mode = DGILibDiscovery.set_mode

# # Housekeeping
# housekeeping = DGILibHousekeeping
# connect = DGILibHousekeeping.connect
# disconnect = DGILibHousekeeping.disconnect
# connection_status = DGILibHousekeeping.connection_status
# get_major_version = DGILibHousekeeping.get_major_version
# get_minor_version = DGILibHousekeeping.get_minor_version
# get_build_number = DGILibHousekeeping.get_build_number
# get_fw_version = DGILibHousekeeping.get_fw_version
# start_polling = DGILibHousekeeping.start_polling
# stop_polling = DGILibHousekeeping.stop_polling
# target_reset = DGILibHousekeeping.target_reset

# # Interface communication
# interface_communication = DGILibInterfaceCommunication
# interface_list = DGILibInterfaceCommunication.interface_list
# interface_enable = DGILibInterfaceCommunication.interface_enable
# interface_disable = DGILibInterfaceCommunication.interface_disable
# interface_get_configuration = DGILibInterfaceCommunication.interface_get_configuration
# interface_set_configuration = DGILibInterfaceCommunication.interface_set_configuration
# interface_clear_buffer = DGILibInterfaceCommunication.interface_clear_buffer
# interface_read_data = DGILibInterfaceCommunication.interface_read_data
# interface_write_data = DGILibInterfaceCommunication.interface_write_data

# # Auxilary
# auxiliary = DGILibAuxiliary
# auxiliary_power_initialize = DGILibAuxiliary.auxiliary_power_initialize
# auxiliary_power_uninitialize = DGILibAuxiliary.auxiliary_power_uninitialize
# auxiliary_power_register_buffer_pointers = DGILibAuxiliary.auxiliary_power_register_buffer_pointers
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


class TestPyDGILib(unittest.TestCase):
    """Tests for PyDGILib."""

    def test_get_major_version(self):
        """test_get_major_version."""
        with DGILib(dgilib_path) as dgilib:
            self.assertIsInstance(dgilib.get_major_version(), int)

    def test_get_minor_version(self):
        """test_get_minor_version."""
        with DGILib(dgilib_path) as dgilib:
            self.assertIsInstance(dgilib.get_minor_version(), int)

    def test_get_build_number(self):
        """test_get_build_number."""
        with DGILib(dgilib_path) as dgilib:
            self.assertIsInstance(dgilib.get_build_number(), int)

    def test_get_device_name(self):
        """test_get_device_name."""
        with DGILib(dgilib_path) as dgilib:
            self.assertIsInstance(dgilib.get_device_name(0), bytes)

    def test_get_fw_version(self):
        """test_get_fw_version."""
        with DGILib(dgilib_path) as dgilib:
            major_fw, minor_fw = dgilib.get_fw_version()
            self.assertIsInstance(major_fw, int)
            self.assertIsInstance(minor_fw, int)

    def test_device_sn(self):
        """test_device_sn."""
        with DGILib(dgilib_path) as dgilib:
            self.assertIsInstance(dgilib.device_sn, bytes)
            self.assertEqual(len(dgilib.device_sn), 20)

    def test_is_msd_mode(self):
        """test_is_msd_mode."""
        with DGILib(dgilib_path) as dgilib:
            self.assertFalse(dgilib.is_msd_mode(dgilib.get_device_name(0)))

    def test_connection_status(self):
        """test_connection_status."""
        with DGILib(dgilib_path) as dgilib:
            self.assertIsInstance(dgilib.connection_status(), int)

    def test_import_and_measure(self):
        """test_import_and_measure."""
        data = []
        data_obj = []

        config_dict = {
            "dgilib_path": dgilib_path,
            "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
            "power_buffers": [
                {"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
            "read_mode": [True, True, True, True],
            "write_mode": [False, False, False, False],
            "loggers": [LOGGER_CSV, LOGGER_OBJECT],
            "verbose": 0,
        }

        with DGILibExtra(**config_dict) as dgilib:
            data = dgilib.logger.log(1)
            data_obj = dgilib.data

        self.assertEqual(len(data), len(data_obj))
        # assert(len(tuple(data[INTERFACE_POWER]))
        #        == len(data_obj[INTERFACE_POWER]))
        # assert(len(data[INTERFACE_GPIO]) == len(data_obj[INTERFACE_GPIO]))
        # assert(tuple(data[INTERFACE_POWER])[0] == data_obj[INTERFACE_POWER][0])
        # assert(tuple(data[INTERFACE_POWER])[1] == data_obj[INTERFACE_POWER][1])
        # assert(data[INTERFACE_GPIO][0] == data_obj[INTERFACE_GPIO][0])
        # assert(data[INTERFACE_GPIO][1] == data_obj[INTERFACE_GPIO][1])

    def test_calculate_average(self):
        """test_calculate_average."""
        assert(calculate_average([[0, 2], [500, 2]]) == 2)

    def test_gpio_augment_edges(self):
        """test_gpio_augment_edges."""
        config_dict = {
            "dgilib_path": dgilib_path,
            "interfaces": [INTERFACE_POWER, INTERFACE_GPIO],
            "power_buffers": [
                {"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
            "read_mode": [True, True, True, True],
            "write_mode": [False, False, False, False],
            "loggers": [LOGGER_CSV, LOGGER_OBJECT],
            "verbose": 0,
        }

        with DGILibExtra(**config_dict) as dgilib:
            dgilib.logger.log(1)
            # gpio_augment_edges(dgilib.data[INTERFACE_GPIO])

    def test_mergeData(self):
        """test_mergeData."""
        data = {INTERFACE_POWER: [], INTERFACE_GPIO: []}
        data1 = {INTERFACE_POWER: [2], INTERFACE_GPIO: [3]}
        mergeData(data, data1)
