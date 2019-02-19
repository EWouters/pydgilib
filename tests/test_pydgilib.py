from pydgilib_extra import *

dgilib_path = "C:\\Users\\erikw_000\\Documents\\GitHub\\Atmel-SAML11\\Python\\dgilib.dll"


class TestPyDGILib(object):
    def test_get_major_version(self):
        with DGILib(dgilib_path, verbose=0) as dgilib:
            assert(type(dgilib.get_major_version()) is int)
    
    def test_get_minor_version(self):
        with DGILib(dgilib_path, verbose=0) as dgilib:
            assert(type(dgilib.get_minor_version()) is int)
    
    def test_get_build_number(self):
        with DGILib(dgilib_path, verbose=0) as dgilib:
            assert(type(dgilib.get_build_number()) is int)
    
    def test_get_build_number(self):
        with DGILib(dgilib_path, verbose=0) as dgilib:
            assert(type(dgilib.get_device_name(0)) is bytes)
    
    def test_get_fw_version(self):
        with DGILib(dgilib_path, verbose=0) as dgilib:
            major_fw, minor_fw = dgilib.get_fw_version()
            assert(type(major_fw) is int)
            assert(type(minor_fw) is int)

    def test_is_msd_mode(self):
        with DGILib(dgilib_path, verbose=0) as dgilib:
            assert(not dgilib.is_msd_mode(dgilib.get_device_name(0)))

    def test_connection_status(self):
        with DGILib(dgilib_path, verbose=0) as dgilib:
            assert(type(dgilib.connection_status()) is int)
    
    
        # print(dgilib.start_polling())
        # print(dgilib.stop_polling())
        # print(dgilib.target_reset(True))
        # sleep(0.5)
        # print(dgilib.target_reset(False))

        # interface_list = dgilib.interface_list()
        # for interface_id in (INTERFACE_SPI, INTERFACE_USART, INTERFACE_I2C, INTERFACE_GPIO):
        #     if interface_id in interface_list:
        #         print(dgilib.interface_enable(interface_id))
        # dgilib.start_polling()

        # for interface_id in interface_list:
        #     print(dgilib.interface_get_configuration(interface_id))
        # for interface_id in (
        #     INTERFACE_TIMESTAMP,
        #     INTERFACE_SPI,
        #     INTERFACE_USART,
        #     INTERFACE_I2C,
        #     INTERFACE_GPIO,
        #     INTERFACE_POWER_SYNC,
        #     INTERFACE_RESERVED,
        # ):
        #     if interface_id in interface_list:
        #         print(
        #             dgilib.interface_set_configuration(
        #                 interface_id, *dgilib.interface_get_configuration(interface_id)
        #             )
        #         )

        # for interface_id in (INTERFACE_SPI, INTERFACE_USART, INTERFACE_I2C, INTERFACE_GPIO, INTERFACE_POWER_DATA, INTERFACE_POWER_SYNC, INTERFACE_RESERVED):
        #     if interface_id in interface_list:
        #         print(dgilib.interface_read_data(interface_id))
                
        # # TODO: test write data
                
        # dgilib.stop_polling()
        # for interface_id in interface_list:
        #     print(dgilib.interface_clear_buffer(interface_id))

        # for interface_id in (INTERFACE_SPI, INTERFACE_USART, INTERFACE_I2C, INTERFACE_GPIO):
        #     if interface_id in interface_list:
        #         print(dgilib.interface_disable(interface_id))
                

    def test_import_and_measure(self):
        data = []
        data_obj = []

        config_dict = {
            "dgilib_path": dgilib_path,
            "power_buffers": [{"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
            "read_mode": [True, True, True, True],
            "write_mode": [False, False, False, False],
            "loggers": [LOGGER_CSV, LOGGER_OBJECT],
            "verbose": 0,
        }

        with DGILibExtra(**config_dict) as dgilib:
            data = dgilib.logger(1)
            data_obj = dgilib.data

        assert(len(data) == len(data_obj))
        assert(len(data[INTERFACE_POWER]) == len(data_obj[INTERFACE_POWER]))
        assert(len(data[INTERFACE_GPIO]) == len(data_obj[INTERFACE_GPIO]))
        assert(data[INTERFACE_POWER][0] == data_obj[INTERFACE_POWER][0])
        assert(data[INTERFACE_POWER][1] == data_obj[INTERFACE_POWER][1])
        assert(data[INTERFACE_GPIO][0] == data_obj[INTERFACE_GPIO][0])
        assert(data[INTERFACE_GPIO][1] == data_obj[INTERFACE_GPIO][1])

    def test_calculate_average(self):
        assert(calculate_average([[0,2],[500,2]]) == 2)