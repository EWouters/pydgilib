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
        assert(len(tuple(data[INTERFACE_POWER])) == len(data_obj[INTERFACE_POWER]))
        assert(len(data[INTERFACE_GPIO]) == len(data_obj[INTERFACE_GPIO]))
        assert(tuple(data[INTERFACE_POWER])[0] == data_obj[INTERFACE_POWER][0])
        assert(tuple(data[INTERFACE_POWER])[1] == data_obj[INTERFACE_POWER][1])
        assert(data[INTERFACE_GPIO][0] == data_obj[INTERFACE_GPIO][0])
        assert(data[INTERFACE_GPIO][1] == data_obj[INTERFACE_GPIO][1])

    def test_calculate_average(self):
        assert(calculate_average([[0, 2], [500, 2]]) == 2)

    def test_gpio_augment_edges(self):
        config_dict = {
            "dgilib_path": dgilib_path,
            "power_buffers": [{"channel": CHANNEL_A, "power_type": POWER_CURRENT}],
            "read_mode": [True, True, True, True],
            "write_mode": [False, False, False, False],
            "loggers": [LOGGER_CSV, LOGGER_OBJECT],
            "verbose": 0,
        }

        with DGILibExtra(**config_dict) as dgilib:
            dgilib.logger(1)
            gpio_augment_edges(dgilib.data[INTERFACE_GPIO])

    def test_mergeData(self):
        data = {INTERFACE_POWER: [], INTERFACE_GPIO: []}
        data1 = {INTERFACE_POWER: [2], INTERFACE_GPIO: [3]}
        mergeData(data, data1)


class TestInterfaceData(object):
    """Test all funtions of the InterfaceData class."""

    def test_new_interface_data(self):
        """Test instantiations."""
        # Simple instantiaton
        data = InterfaceData()
        assert tuple(data) == (), "Incorrect value"

        # Instantiation from tuple
        data = InterfaceData(([], []))
        assert tuple(data) == (), "Incorrect value"

        # Instantiation from list
        data = InterfaceData([[1], [2]])
        assert tuple(data) == ((1, 2),), "Incorrect value"

        # Instantiation from tuple
        data = InterfaceData(([1], [2]))
        assert tuple(data) == ((1, 2),), "Incorrect value"

        # Instantiation from tuple
        data = InterfaceData(([1, 2], [3, 4]))
        assert tuple(data) == ((1, 3), (2, 4),), "Incorrect value"

        # try catch assert error?

    def test__getattr__(self):
        """Tests for timestamps and values functionality."""
        # Simple instantiaton
        data = InterfaceData()
        assert data.timestamps == [], "Incorrect value"
        assert data.values == [], "Incorrect value"
        assert data["timestamps"] == [], "Incorrect value"
        assert data["values"] == [], "Incorrect value"

        # Instantiation from tuple
        data = InterfaceData(([], []))
        assert data.timestamps == [], "Incorrect value"
        assert data.values == [], "Incorrect value"
        assert data["timestamps"] == [], "Incorrect value"
        assert data["values"] == [], "Incorrect value"

        # Instantiation from list
        data = InterfaceData([[1], [2]])
        assert data.timestamps == [1], "Incorrect value"
        assert data.values == [2], "Incorrect value"
        assert data["timestamps"] == [1], "Incorrect value"
        assert data["values"] == [2], "Incorrect value"

        # Instantiation from tuple
        data = InterfaceData(([1], [2]))
        assert data.timestamps == [1], "Incorrect value"
        assert data.values == [2], "Incorrect value"
        assert data["timestamps"] == [1], "Incorrect value"
        assert data["values"] == [2], "Incorrect value"

        # Instantiation from tuple
        data = InterfaceData(([1, 2], [3, 4]))
        assert data.timestamps == [1, 2], "Incorrect value"
        assert data.values == [3, 4], "Incorrect value"
        assert data["timestamps"] == [1, 2], "Incorrect value"
        assert data["values"] == [3, 4], "Incorrect value"
        assert data[0] == (1, 3), "Incorrect value"
        assert data[1] == (2, 4), "Incorrect value"

        # Getting as tuple
        assert tuple(data) == ((1, 3), (2, 4),), "Incorrect value"

    def test__setattr__(self):
        """Tests for timestamps and values functionality."""
        data = InterfaceData([[1], [2]])

        # Setting as tuple (not recommended)
        data["timestamps"][0] = 3
        assert tuple(data) == ((3, 2),), "Incorrect value"

        # Setting as attribute (not recommended)
        data.values[0] = 4
        assert tuple(data) == ((3, 4),), "Incorrect value"

    def test__iadd__(self):
        """Tests for __iadd__ function."""
        # Add tuple for existing interface
        data = InterfaceData([[1], [2]])
        data += ([2], [3])
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"
        # Add list for existing interface
        data += [[3], [4]]
        assert tuple(data) == ((1, 2), (2, 3), (3, 4)), "Incorrect value"
        # Add InterfaceData for existing interface
        data = InterfaceData([[1], [2]])
        data += InterfaceData([[2, 3], [3, 4]])
        assert tuple(data) == ((1, 2), (2, 3), (3, 4)), "Incorrect value"

    def test__add__(self):
        """Tests for __add__ function."""
        # Simple addition of objects
        data1 = InterfaceData([[1], [2]])
        data2 = InterfaceData([[2], [3]])
        data = data1 + data2
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"
        # Check that data has been deep copied
        data1 = InterfaceData(([4], [5]))
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"
        # Delete original copies (decrease reference count to them)
        del data1
        del data2
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"
        # Check that data has been shallow copied
        data = InterfaceData([[1], [2]])
        data1 = data
        data += InterfaceData([[3], [4]])
        assert tuple(data1) == ((1, 2), (3, 4)), "Incorrect value"
        # Check that data has been deep copied
        data = InterfaceData([[1], [2]])
        data1 = data + InterfaceData()
        data += InterfaceData([[3], [4]])
        assert tuple(data1) == ((1, 2),), "Incorrect value"

    def test_extend(self):
        """Tests for extend function."""
        # Simple extention of objects
        data = InterfaceData([[1], [2]])
        data1 = InterfaceData([[2], [3]])
        data.extend(data1)
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"
        # Extention with empty lists and tuples
        data = InterfaceData([[1], [2]])
        data.extend(InterfaceData())
        assert tuple(data) == ((1, 2),), "Incorrect value"
        data.extend(InterfaceData(([], [])))
        assert tuple(data) == ((1, 2),), "Incorrect value"
        data.extend(InterfaceData([[], []]))
        assert tuple(data) == ((1, 2),), "Incorrect value"
        data.extend(([], []))
        assert tuple(data) == ((1, 2),), "Incorrect value"
        data.extend([[], []])
        assert tuple(data) == ((1, 2),), "Incorrect value"
        # Extention with non-empty lists and tuples
        data = InterfaceData([[1], [2]])
        data.extend(InterfaceData())
        assert tuple(data) == ((1, 2),), "Incorrect value"
        data = InterfaceData([[1], [2]])
        data.extend(InterfaceData(([2], [3])))
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"
        data = InterfaceData([[1], [2]])
        data.extend(InterfaceData([[2], [3]]))
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"
        data = InterfaceData([[1], [2]])
        data.extend(([2], [3]))
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"
        data = InterfaceData([[1], [2]])
        data.extend([[2], [3]])
        assert tuple(data) == ((1, 2), (2, 3)), "Incorrect value"

    def test__len__(self):
        """Tests for __len__ function."""
        # Simple instantiaton
        data = InterfaceData()
        assert len(data) == 0, "Incorrect length"

        # Instantiation from tuple
        data = InterfaceData(([], []))
        assert len(data) == 0, "Incorrect length"

        # Instantiation from list
        data = InterfaceData([[1], [2]])
        assert len(data) == 1, "Incorrect length"

        # Instantiation from tuple
        data = InterfaceData(([1], [2]))
        assert len(data) == 1, "Incorrect length"

        # Instantiation from tuple
        data = InterfaceData(([1, 2], [3, 4]))
        assert len(data) == 2, "Incorrect length"

    def test__getitem__(self):
        """Tests for __getitem__ function."""
        # Simple instantiaton
        data = InterfaceData(([1, 2], [3, 4]))
        assert data[0] == (1, 3), "Incorrect value"
        assert data[1] == (2, 4), "Incorrect value"

    def test_valid_interface_data(self):
        """Tests for valid_interface_data function."""
        assert not valid_interface_data([]), "Incorrect tuple accepted"
        assert valid_interface_data(([], [])), "Incorrect tuple rejection"
        assert not valid_interface_data(
            ([], [], [])), "Incorrect tuple accepted"
        assert not valid_interface_data(([])), "Incorrect tuple accepted"
        assert not valid_interface_data(([1], [])), "Incorrect tuple accepted"
        assert not valid_interface_data(([], [1])), "Incorrect tuple accepted"
        assert valid_interface_data(([1], [2])), "Incorrect tuple rejection"
        assert valid_interface_data(
            ([1, 2], [2, 3])), "Incorrect tuple rejection"


class TestLoggerData(object):
    """Test all funtions of the LoggerData class."""

    def test_init_logger_data(self):
        """Test instantiations."""
        # Simple instantiaton
        data = LoggerData()
        assert tuple(data[INTERFACE_POWER]) == (), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == (), "Incorrect value"

        # Instantiaton from list of interfaces
        data = LoggerData([INTERFACE_GPIO, INTERFACE_POWER])
        assert tuple(data[INTERFACE_POWER]) == (), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == (), "Incorrect value"

        # Instantiation from dictionary with empty values
        data = LoggerData(
            {INTERFACE_POWER: InterfaceData(), INTERFACE_GPIO: InterfaceData()})
        assert tuple(data[INTERFACE_POWER]) == (), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == (), "Incorrect value"

        # Instantiation from dictionary
        data = LoggerData(
            {INTERFACE_POWER: ([], []), INTERFACE_GPIO: ([], [])})
        assert tuple(data[INTERFACE_POWER]) == (), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == (), "Incorrect value"

        # Instantiation from dictionary with data
        data = LoggerData(
            {INTERFACE_POWER: ([1], [2]), INTERFACE_GPIO: ([3], [4])})
        assert tuple(data[INTERFACE_POWER]) == ((1, 2),), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == ((3, 4),), "Incorrect value"

        # Instantiation from dictionary with InterfaceData
        data = LoggerData({
            INTERFACE_POWER: InterfaceData(([1], [2])),
            INTERFACE_GPIO: InterfaceData(([3], [4]))})
        assert tuple(data[INTERFACE_POWER]) == ((1, 2),), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == ((3, 4),), "Incorrect value"

    def test__getattr__(self):
        """Tests for __getattr__ function."""
        data = LoggerData({
            INTERFACE_POWER: ([1], [2]),
            INTERFACE_GPIO: ([], []),
            4: ([3, 4], [5, 6])})

        # Getting via dict
        assert tuple(data[INTERFACE_POWER]) == ((1, 2),), "Incorrect value"
        # Getting via attribute
        assert tuple(data.gpio) == (), "Incorrect value"
        # assert data["gpio"] == ([3], [4]) # Not in syntax

    def test__setattr__(self):
        """Tests for __setattr__ function."""
        data = LoggerData({INTERFACE_POWER: ([1], [2])})

        # Setting as dict
        data[INTERFACE_GPIO] = InterfaceData(([3], [4]))
        assert tuple(data[INTERFACE_POWER]) == ((1, 2),), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == ((3, 4),), "Incorrect value"

        # Setting as attribute
        data.spi = InterfaceData(([5], [6]))
        assert tuple(data[INTERFACE_SPI]) == ((5, 6),), "Incorrect value"

    def test__iadd__(self):
        """Tests for __iadd__ function."""
        # Add dict for existing interface
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data += {INTERFACE_POWER: ([2], [3])}
        assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3)), "Incorrect value"
        # Add LoggerData for existing interface
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data += LoggerData({INTERFACE_POWER: ([2], [3])})
        assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3)), "Incorrect value"

        # Add dict and LoggerData with new interfaces
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data += {INTERFACE_GPIO: ([2], [3])}
        data += LoggerData({4: ([3], [4])})
        assert tuple(data[INTERFACE_POWER]) == ((1, 2),), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == ((2, 3),), "Incorrect value"
        assert tuple(data[4]) == ((3, 4),), "Incorrect value"

        # Add dict and LoggerData for new and existing interfaces
        data = LoggerData({
            INTERFACE_POWER: ([1], [2]),
            4: ([3, 4], [5, 6])})
        data += {
            INTERFACE_POWER: ([2], [3]), INTERFACE_GPIO: ([2], [3])}
        data += LoggerData({INTERFACE_POWER: ([3], [4]),
                            INTERFACE_GPIO: ([1], [2])})
        assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3), (3, 4)), "Incorrect value"
        assert tuple(data[INTERFACE_GPIO]) == (
            (2, 3), (1, 2)), "Incorrect value"
        assert tuple(data[4]) == ((3, 5), (4, 6)), "Incorrect value"

    def test__add__(self):
        """Tests for __add__ function."""
        # Simple addition of objects
        data1 = LoggerData({INTERFACE_POWER: ([1], [2])})
        data2 = LoggerData({INTERFACE_POWER: ([2], [3])})
        data = data1 + data2
        assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3)), "Incorrect value"
        # Check that data has been deep copied
        data1[INTERFACE_POWER] = ([4], [5])
        assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3)), "Incorrect value"
        # Delete original copies (decrease reference count to them)
        del data1
        del data2
        assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3)), "Incorrect value"
        # # Check that data has been shallow copied
        # data = LoggerData({INTERFACE_POWER: ([1], [2])}), "Incorrect value"
        # data1 = data
        # del data
        # assert data1[INTERFACE_POWER] == ((1, 2),), "Incorrect value"
        # Check that data has been deep copied
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data1 = data + {}
        del data
        assert tuple(data1[INTERFACE_POWER]) == ((1, 2),), "Incorrect value"

    def test_extend(self):
        """Tests for extend function."""
        # Simple extention of objects
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data1 = InterfaceData([[2], [3]])
        data.extend(INTERFACE_POWER, data1)
        assert tuple(data[INTERFACE_POWER]) == (
            (1, 2), (2, 3)), "Incorrect value"

    def test_length(self):
        """Tests for length function."""
        data = LoggerData({
            INTERFACE_POWER: ([1], [2]),
            INTERFACE_GPIO: ([], []),
            4: ([3, 4], [5, 6])})
        # Lenght of individual interfaces
        assert data.length(INTERFACE_POWER) == 1, "Incorrect length"
        assert data.length(INTERFACE_GPIO) == 0, "Incorrect length"
        assert data.length(4) == 2, "Incorrect length"

        # Lenghts in dict of interfaces
        len_dict = data.length()
        assert len_dict[INTERFACE_POWER] == 1, "Incorrect length"
        assert len_dict[INTERFACE_GPIO] == 0, "Incorrect length"
        assert len_dict[4] == 2, "Incorrect length"
