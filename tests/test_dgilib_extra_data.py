"""This module holds the automated tests for DGILibExtra Data."""

from pydgilib_extra import (InterfaceData, LoggerData, valid_interface_data,
                            INTERFACE_POWER, INTERFACE_SPI, INTERFACE_GPIO)
import unittest


class TestInterfaceData(unittest.TestCase):
    """Test all functions of the InterfaceData class."""

    def test_new_interface_data(self):
        """Test instantiations."""
        # Simple instantiaton
        data = InterfaceData()
        self.assertEqual(tuple(data), ())

        # Instantiation from tuple
        data = InterfaceData(([], []))
        self.assertEqual(tuple(data), ())

        # Instantiation from list
        data = InterfaceData([[1], [2]])
        self.assertEqual(tuple(data), ((1, 2),))

        # Instantiation from tuple
        data = InterfaceData(([1], [2]))
        self.assertEqual(tuple(data), ((1, 2),))

        # Instantiation from tuple
        data = InterfaceData(([1, 2], [3, 4]))
        self.assertEqual(tuple(data), ((1, 3), (2, 4),))

        # Instantiation from two lists
        data = InterfaceData([1, 2], [3, 4])
        self.assertEqual(tuple(data), ((1, 3), (2, 4),))

        # Instantiation from two ints
        data = InterfaceData(1, 2)
        self.assertEqual(tuple(data), ((1, 2),))

        # try catch assert error?
        # assertRaises()
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertRaises

    def test__getattr__(self):
        """Tests for timestamps and values functionality."""
        # Simple instantiaton
        data = InterfaceData()
        self.assertEqual(data.timestamps, [])
        self.assertEqual(data.values, [])

        # Instantiation from tuple
        data = InterfaceData(([], []))
        self.assertEqual(data.timestamps, [])
        self.assertEqual(data.values, [])

        # Instantiation from list
        data = InterfaceData([[1], [2]])
        self.assertEqual(data.timestamps, [1])
        self.assertEqual(data.values, [2])

        # Instantiation from tuple
        data = InterfaceData(([1], [2]))
        self.assertEqual(data.timestamps, [1])
        self.assertEqual(data.values, [2])

        # Instantiation from tuple
        data = InterfaceData(([1, 2], [3, 4]))
        self.assertEqual(data.timestamps, [1, 2])
        self.assertEqual(data.values, [3, 4])
        self.assertEqual(data[0], (1, 3))
        self.assertEqual(data[1], (2, 4))

        # Getting as tuple
        self.assertEqual(tuple(data), ((1, 3), (2, 4),))

    def test__setattr__(self):
        """Tests for timestamps and values functionality."""
        data = InterfaceData([[1], [2]])

        # Setting as tuple (not recommended)
        data.timestamps[0] = 3
        self.assertEqual(tuple(data), ((3, 2),))

        # Setting as attribute (not recommended)
        data.values[0] = 4
        self.assertEqual(tuple(data), ((3, 4),))

    def test__iadd__(self):
        """Tests for __iadd__ function."""
        # Add tuple for existing interface
        data = InterfaceData([[1], [2]])
        data += ([2], [3])
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))
        # Add list for existing interface
        data += [[3], [4]]
        self.assertEqual(tuple(data), ((1, 2), (2, 3), (3, 4)))
        # Add InterfaceData for existing interface
        data = InterfaceData([[1], [2]])
        data += InterfaceData([[2, 3], [3, 4]])
        self.assertEqual(tuple(data), ((1, 2), (2, 3), (3, 4)))

    def test__add__(self):
        """Tests for __add__ function."""
        # Simple addition of objects
        data1 = InterfaceData([[1], [2]])
        data2 = InterfaceData([[2], [3]])
        data = data1 + data2
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))
        # Check that data has been deep copied
        data1 = InterfaceData(([4], [5]))
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))
        # Delete original copies (decrease reference count to them)
        del data1
        del data2
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))
        # Check that data has been shallow copied
        data = InterfaceData([[1], [2]])
        data1 = data
        data += InterfaceData([[3], [4]])
        self.assertEqual(tuple(data1), ((1, 2), (3, 4)))
        # Check that data has been deep copied
        data = InterfaceData([[1], [2]])
        data1 = data + InterfaceData()
        data += InterfaceData([[3], [4]])
        self.assertEqual(tuple(data1), ((1, 2),))

    def test_extend(self):
        """Tests for extend function."""
        # Simple extention of objects
        data = InterfaceData([[1], [2]])
        data1 = InterfaceData([[2], [3]])
        data.extend(data1)
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))
        # Extention with empty lists and tuples
        data = InterfaceData([[1], [2]])
        data.extend(InterfaceData())
        self.assertEqual(tuple(data), ((1, 2),))
        data.extend(InterfaceData(([], [])))
        self.assertEqual(tuple(data), ((1, 2),))
        data.extend(InterfaceData([[], []]))
        self.assertEqual(tuple(data), ((1, 2),))
        data.extend(([], []))
        self.assertEqual(tuple(data), ((1, 2),))
        data.extend([[], []])
        self.assertEqual(tuple(data), ((1, 2),))
        # Extention with non-empty lists and tuples
        data = InterfaceData([[1], [2]])
        data.extend(InterfaceData())
        self.assertEqual(tuple(data), ((1, 2),))
        data = InterfaceData([[1], [2]])
        data.extend(InterfaceData(([2], [3])))
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))
        data = InterfaceData([[1], [2]])
        data.extend(InterfaceData([[2], [3]]))
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))
        data = InterfaceData([[1], [2]])
        data.extend(([2], [3]))
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))
        data = InterfaceData([[1], [2]])
        data.extend([[2], [3]])
        self.assertEqual(tuple(data), ((1, 2), (2, 3)))

    def test__len__(self):
        """Tests for __len__ function."""
        # Simple instantiaton
        data = InterfaceData()
        self.assertEqual(len(data), 0)

        # Instantiation from tuple
        data = InterfaceData(([], []))
        self.assertEqual(len(data), 0)

        # Instantiation from list
        data = InterfaceData([[1], [2]])
        self.assertEqual(len(data), 1)

        # Instantiation from tuple
        data = InterfaceData(([1], [2]))
        self.assertEqual(len(data), 1)

        # Instantiation from tuple
        data = InterfaceData(([1, 2], [3, 4]))
        self.assertEqual(len(data), 2)

    def test__getitem__(self):
        """Tests for __getitem__ function."""
        data = InterfaceData(([1, 2], [3, 4]))
        self.assertEqual(data[0], (1, 3))
        self.assertEqual(data[1], (2, 4))
        self.assertEqual(data[::-1], ([2, 1], [4, 3]))
        data.append([[9, 8, 7, 6], [34, 45, 56, 67]])
        self.assertEqual(data[4:6], ([7, 6], [56, 67]))

        # Loops
        for timestamp, value in data:
            self.assertEqual(timestamp, 1)
            self.assertEqual(value, 3)
            break
        for timestamp, value in reversed(data):
            self.assertEqual(timestamp, 6)
            self.assertEqual(value, 67)
            break
        for sample in data:
            self.assertIn(InterfaceData(*sample), data)

    def test__contains__(self):
        """Tests for __contains__ function."""
        data = InterfaceData(([1, 2], [3, 4]))
        self.assertIn(([2], [4]), data)
        self.assertNotIn(([9], [34]), data)
        self.assertIn(([], []), data)
        self.assertIn(data, data + ([10], [34]))
        self.assertNotIn(data + ([10], [34]), data)
        self.assertIn(data + ([10], [34]), data + ([10], [34]))

    def test_valid_interface_data(self):
        """Tests for valid_interface_data function."""
        self.assertTrue(valid_interface_data(([], [])))
        self.assertTrue(valid_interface_data(([1], [2])))
        self.assertTrue(valid_interface_data(([1, 2], [2, 3])))

        self.assertFalse(valid_interface_data([]))
        self.assertFalse(valid_interface_data(([], [], [])))
        self.assertFalse(valid_interface_data(([])))
        self.assertFalse(valid_interface_data(([1], [])))
        self.assertFalse(valid_interface_data(([], [1])))


class TestLoggerData(unittest.TestCase):
    """Test all functions of the LoggerData class."""

    def test_init_logger_data(self):
        """Test instantiations."""
        # Simple instantiaton
        data = LoggerData()
        self.assertEqual(tuple(data[INTERFACE_POWER]), ())
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ())

        # Instantiaton from list of interfaces
        data = LoggerData([INTERFACE_GPIO, INTERFACE_POWER])
        self.assertEqual(tuple(data[INTERFACE_POWER]), ())
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ())

        # Instantiation from dictionary with empty values
        data = LoggerData(
            {INTERFACE_POWER: InterfaceData(), INTERFACE_GPIO: InterfaceData()}
        )
        self.assertEqual(tuple(data[INTERFACE_POWER]), ())
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ())

        # Instantiation from dictionary
        data = LoggerData(
            {INTERFACE_POWER: ([], []), INTERFACE_GPIO: ([], [])})
        self.assertEqual(tuple(data[INTERFACE_POWER]), ())
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ())

        # Instantiation from dictionary with data
        data = LoggerData(
            {INTERFACE_POWER: ([1], [2]), INTERFACE_GPIO: ([3], [4])})
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2),))
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ((3, 4),))

        # Instantiation from dictionary with InterfaceData
        data = LoggerData({
            INTERFACE_POWER: InterfaceData(([1], [2])),
            INTERFACE_GPIO: InterfaceData(([3], [4]))})
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2),))
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ((3, 4),))

    def test__getattr__(self):
        """Tests for __getattr__ function."""
        data = LoggerData({
            INTERFACE_POWER: ([1], [2]),
            INTERFACE_GPIO: ([], []),
            4: ([3, 4], [5, 6])})

        # Getting via dict
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2),))
        # Getting via attribute
        self.assertEqual(tuple(data.gpio), ())
        # assert data["gpio"] == ([3], [4]) # Not in syntax

    def test__setattr__(self):
        """Tests for __setattr__ function."""
        data = LoggerData({INTERFACE_POWER: ([1], [2])})

        # Setting as dict
        data[INTERFACE_GPIO] = InterfaceData(([3], [4]))
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2),))
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ((3, 4),))

        # Setting as attribute
        data.spi = InterfaceData(([5], [6]))
        self.assertEqual(tuple(data[INTERFACE_SPI]), ((5, 6),))

    def test__iadd__(self):
        """Tests for __iadd__ function."""
        # Add dict for existing interface
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data += {INTERFACE_POWER: ([2], [3])}
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2), (2, 3)))
        # Add LoggerData for existing interface
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data += LoggerData({INTERFACE_POWER: ([2], [3])})
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2), (2, 3)))

        # Add dict and LoggerData with new interfaces
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data += {INTERFACE_GPIO: ([2], [3])}
        data += LoggerData({4: ([3], [4])})
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2),))
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ((2, 3),))
        self.assertEqual(tuple(data[4]), ((3, 4),))

        # Add dict and LoggerData for new and existing interfaces
        data = LoggerData({
            INTERFACE_POWER: ([1], [2]),
            4: ([3, 4], [5, 6])})
        data += {
            INTERFACE_POWER: ([2], [3]), INTERFACE_GPIO: ([2], [3])}
        data += LoggerData({INTERFACE_POWER: ([3], [4]),
                            INTERFACE_GPIO: ([1], [2])})
        self.assertEqual(tuple(data[INTERFACE_POWER]),
                         ((1, 2), (2, 3), (3, 4)))
        self.assertEqual(tuple(data[INTERFACE_GPIO]), ((2, 3), (1, 2)))
        self.assertEqual(tuple(data[4]), ((3, 5), (4, 6)))

    def test__add__(self):
        """Tests for __add__ function."""
        # Simple addition of objects
        data1 = LoggerData({INTERFACE_POWER: ([1], [2])})
        data2 = LoggerData({INTERFACE_POWER: ([2], [3])})
        data = data1 + data2
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2), (2, 3)))
        # Check that data has been deep copied
        data1[INTERFACE_POWER] = ([4], [5])
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2), (2, 3)))
        # Delete original copies (decrease reference count to them)
        del data1
        del data2
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2), (2, 3)))
        # # Check that data has been shallow copied
        # data = LoggerData({INTERFACE_POWER: ([1], [2])}), "Incorrect value"
        # data1 = data
        # del data
        # assert data1[INTERFACE_POWER] == ((1, 2),), "Incorrect value"
        # Check that data has been deep copied
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data1 = data + {}
        del data
        self.assertEqual(tuple(data1[INTERFACE_POWER]), ((1, 2),))

    def test_extend(self):
        """Tests for extend function."""
        # Simple extention of objects
        data = LoggerData({INTERFACE_POWER: ([1], [2])})
        data1 = InterfaceData([[2], [3]])
        data.extend(INTERFACE_POWER, data1)
        self.assertEqual(tuple(data[INTERFACE_POWER]), ((1, 2), (2, 3)))

    def test_length(self):
        """Tests for length function."""
        data = LoggerData({
            INTERFACE_POWER: ([1], [2]),
            INTERFACE_GPIO: ([], []),
            4: ([3, 4], [5, 6])})
        # Length of individual interfaces
        self.assertEqual(data.length(INTERFACE_POWER), 1)
        self.assertEqual(data.length(INTERFACE_GPIO), 0)
        self.assertEqual(data.length(4), 2)

        # Lengths in dict of interfaces
        len_dict = data.length()
        self.assertEqual(len_dict[INTERFACE_POWER], 1)
        self.assertEqual(len_dict[INTERFACE_GPIO], 0)
        self.assertEqual(len_dict[4], 2)
