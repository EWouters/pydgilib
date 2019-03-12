"""This module holds the automated tests for InterfaceData."""

from pydgilib_extra import (InterfaceData, valid_interface_data)


def test_new_interface_data():
    """Test instantiations."""
    # Simple instantiaton
    data = InterfaceData()
    assert tuple(data) == ()

    # Instantiation from tuple
    data = InterfaceData(([], []))
    assert tuple(data) == ()

    # Instantiation from list
    data = InterfaceData([[1], [2]])
    assert tuple(data) == ((1, 2),)

    # Instantiation from tuple
    data = InterfaceData(([1], [2]))
    assert tuple(data) == ((1, 2),)

    # Instantiation from tuple
    data = InterfaceData(([1, 2], [3, 4]))
    assert tuple(data) == ((1, 3), (2, 4),)

    # Instantiation from two lists
    data = InterfaceData([1, 2], [3, 4])
    assert tuple(data) == ((1, 3), (2, 4),)

    # Instantiation from two ints
    data = InterfaceData(1, 2)
    assert tuple(data) == ((1, 2),)

    # try catch assert error?
    # assertRaises()
    # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertRaises


def test__getattr__():
    """Tests for timestamps and values functionality."""
    # Simple instantiaton
    data = InterfaceData()
    assert data.timestamps == []
    assert data.values == []

    # Instantiation from tuple
    data = InterfaceData(([], []))
    assert data.timestamps == []
    assert data.values == []

    # Instantiation from list
    data = InterfaceData([[1], [2]])
    assert data.timestamps == [1]
    assert data.values == [2]

    # Instantiation from tuple
    data = InterfaceData(([1], [2]))
    assert data.timestamps == [1]
    assert data.values == [2]

    # Instantiation from tuple
    data = InterfaceData(([1, 2], [3, 4]))
    assert data.timestamps == [1, 2]
    assert data.values == [3, 4]
    assert data[0] == (1, 3)
    assert data[1] == (2, 4)

    # Getting as tuple
    assert tuple(data) == ((1, 3), (2, 4),)


def test__setattr__():
    """Tests for timestamps and values functionality."""
    data = InterfaceData([[1], [2]])

    # Setting as tuple (not recommended)
    data.timestamps[0] = 3
    assert tuple(data) == ((3, 2),)

    # Setting as attribute (not recommended)
    data.values[0] = 4
    assert tuple(data) == ((3, 4),)


def test__iadd__():
    """Tests for __iadd__ function."""
    # Add tuple for existing interface
    data = InterfaceData([[1], [2]])
    data += ([2], [3])
    assert tuple(data) == ((1, 2), (2, 3))
    # Add list for existing interface
    data += [[3], [4]]
    assert tuple(data) == ((1, 2), (2, 3), (3, 4))
    # Add InterfaceData for existing interface
    data = InterfaceData([[1], [2]])
    data += InterfaceData([[2, 3], [3, 4]])
    assert tuple(data) == ((1, 2), (2, 3), (3, 4))


def test__add__():
    """Tests for __add__ function."""
    # Simple addition of objects
    data1 = InterfaceData([[1], [2]])
    data2 = InterfaceData([[2], [3]])
    data = data1 + data2
    assert tuple(data) == ((1, 2), (2, 3))
    # Check that data has been deep copied
    data1 = InterfaceData(([4], [5]))
    assert tuple(data) == ((1, 2), (2, 3))
    # Delete original copies (decrease reference count to them)
    del data1
    del data2
    assert tuple(data) == ((1, 2), (2, 3))
    # Check that data has been shallow copied
    data = InterfaceData([[1], [2]])
    data1 = data
    data += InterfaceData([[3], [4]])
    assert tuple(data1) == ((1, 2), (3, 4))
    # Check that data has been deep copied
    data = InterfaceData([[1], [2]])
    data1 = data + InterfaceData()
    data += InterfaceData([[3], [4]])
    assert tuple(data1) == ((1, 2),)


def test_extend():
    """Tests for extend function."""
    # Simple extention of objects
    data = InterfaceData([[1], [2]])
    data1 = InterfaceData([[2], [3]])
    data.extend(data1)
    assert tuple(data) == ((1, 2), (2, 3))
    # Extention with empty lists and tuples
    data = InterfaceData([[1], [2]])
    data.extend(InterfaceData())
    assert tuple(data) == ((1, 2),)
    data.extend(InterfaceData(([], [])))
    assert tuple(data) == ((1, 2),)
    data.extend(InterfaceData([[], []]))
    assert tuple(data) == ((1, 2),)
    data.extend(([], []))
    assert tuple(data) == ((1, 2),)
    data.extend([[], []])
    assert tuple(data) == ((1, 2),)
    # Extention with non-empty lists and tuples
    data = InterfaceData([[1], [2]])
    data.extend(InterfaceData())
    assert tuple(data) == ((1, 2),)
    data = InterfaceData([[1], [2]])
    data.extend(InterfaceData(([2], [3])))
    assert tuple(data) == ((1, 2), (2, 3))
    data = InterfaceData([[1], [2]])
    data.extend(InterfaceData([[2], [3]]))
    assert tuple(data) == ((1, 2), (2, 3))
    data = InterfaceData([[1], [2]])
    data.extend(([2], [3]))
    assert tuple(data) == ((1, 2), (2, 3))
    data = InterfaceData([[1], [2]])
    data.extend([[2], [3]])
    assert tuple(data) == ((1, 2), (2, 3))


def test__len__():
    """Tests for __len__ function."""
    # Simple instantiaton
    data = InterfaceData()
    assert len(data) == 0

    # Instantiation from tuple
    data = InterfaceData(([], []))
    assert len(data) == 0

    # Instantiation from list
    data = InterfaceData([[1], [2]])
    assert len(data) == 1

    # Instantiation from tuple
    data = InterfaceData(([1], [2]))
    assert len(data) == 1

    # Instantiation from tuple
    data = InterfaceData(([1, 2], [3, 4]))
    assert len(data) == 2


def test__getitem__():
    """Tests for __getitem__ function."""
    data = InterfaceData(([1, 2], [3, 4]))
    assert data[0] == (1, 3)
    assert data[1] == (2, 4)
    assert data[::-1] == ([2, 1], [4, 3])
    data.append([[9, 8, 7, 6], [34, 45, 56, 67]])
    assert data[4:6] == ([7, 6], [56, 67])

    # Loops
    for timestamp, value in data:
        assert timestamp == 1
        assert value == 3
        break
    for timestamp, value in reversed(data):
        assert timestamp == 6
        assert value == 67
        break
    for sample in data:
        assert InterfaceData(*sample) in data


def test__contains__():
    """Tests for __contains__ function."""
    data = InterfaceData(([1, 2], [3, 4]))
    assert ([2], [4]) in data
    assert ([9], [34]) not in data
    assert ([], []) in data
    assert data in data + ([10], [34])
    assert data + ([10], [34]) not in data
    assert data + ([10], [34]) in data + ([10], [34])


def test_valid_interface_data():
    """Tests for valid_interface_data function."""
    assert valid_interface_data(([], []))
    assert valid_interface_data(([1], [2]))
    assert valid_interface_data(([1, 2], [2, 3]))

    assert not valid_interface_data([])
    assert not valid_interface_data(([], [], []))
    assert not valid_interface_data(([]))
    assert not valid_interface_data(([1], []))
    assert not valid_interface_data(([], [1]))
