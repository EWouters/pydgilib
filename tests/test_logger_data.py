"""This module holds the automated tests for LoggerData."""

from pydgilib_extra import (
    InterfaceData, LoggerData, INTERFACE_POWER, INTERFACE_SPI, INTERFACE_GPIO)


def test_init_logger_data():
    """Test instantiations."""
    # Simple instantiaton
    data = LoggerData()
    assert tuple(data[INTERFACE_POWER]) == ()
    assert tuple(data[INTERFACE_GPIO]) == ()

    # Instantiaton from list of interfaces
    data = LoggerData([INTERFACE_GPIO, INTERFACE_POWER])
    assert tuple(data[INTERFACE_POWER]) == ()
    assert tuple(data[INTERFACE_GPIO]) == ()

    # Instantiation from dictionary with empty values
    data = LoggerData(
        {INTERFACE_POWER: InterfaceData(), INTERFACE_GPIO: InterfaceData()}
    )
    assert tuple(data[INTERFACE_POWER]) == ()
    assert tuple(data[INTERFACE_GPIO]) == ()

    # Instantiation from dictionary
    data = LoggerData(
        {INTERFACE_POWER: ([], []), INTERFACE_GPIO: ([], [])})
    assert tuple(data[INTERFACE_POWER]) == ()
    assert tuple(data[INTERFACE_GPIO]) == ()

    # Instantiation from dictionary with data
    data = LoggerData(
        {INTERFACE_POWER: ([1], [2]), INTERFACE_GPIO: ([3], [4])})
    assert tuple(data[INTERFACE_POWER]) == ((1, 2),)
    assert tuple(data[INTERFACE_GPIO]) == ((3, 4),)

    # Instantiation from dictionary with InterfaceData
    data = LoggerData({
        INTERFACE_POWER: InterfaceData(([1], [2])),
        INTERFACE_GPIO: InterfaceData(([3], [4]))})
    assert tuple(data[INTERFACE_POWER]) == ((1, 2),)
    assert tuple(data[INTERFACE_GPIO]) == ((3, 4),)


def test__getattr__():
    """Tests for __getattr__ function."""
    data = LoggerData({
        INTERFACE_POWER: ([1], [2]),
        INTERFACE_GPIO: ([], []),
        4: ([3, 4], [5, 6])})

    # Getting via dict
    assert tuple(data[INTERFACE_POWER]) == ((1, 2),)
    # Getting via attribute
    assert tuple(data.gpio) == ()
    # assert data["gpio"] == ([3], [4]) # Not in syntax


def test__setattr__():
    """Tests for __setattr__ function."""
    data = LoggerData({INTERFACE_POWER: ([1], [2])})

    # Setting as dict
    data[INTERFACE_GPIO] = InterfaceData(([3], [4]))
    assert tuple(data[INTERFACE_POWER]) == ((1, 2),)
    assert tuple(data[INTERFACE_GPIO]) == ((3, 4),)

    # Setting as attribute
    data.spi = InterfaceData(([5], [6]))
    assert tuple(data[INTERFACE_SPI]) == ((5, 6),)


def test__iadd__():
    """Tests for __iadd__ function."""
    # Add dict for existing interface
    data = LoggerData({INTERFACE_POWER: ([1], [2])})
    data += {INTERFACE_POWER: ([2], [3])}
    assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3))
    # Add LoggerData for existing interface
    data = LoggerData({INTERFACE_POWER: ([1], [2])})
    data += LoggerData({INTERFACE_POWER: ([2], [3])})
    assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3))

    # Add dict and LoggerData with new interfaces
    data = LoggerData({INTERFACE_POWER: ([1], [2])})
    data += {INTERFACE_GPIO: ([2], [3])}
    data += LoggerData({4: ([3], [4])})
    assert tuple(data[INTERFACE_POWER]) == ((1, 2),)
    assert tuple(data[INTERFACE_GPIO]) == ((2, 3),)
    assert tuple(data[4]) == ((3, 4),)

    # Add dict and LoggerData for new and existing interfaces
    data = LoggerData({
        INTERFACE_POWER: ([1], [2]),
        4: ([3, 4], [5, 6])})
    data += {
        INTERFACE_POWER: ([2], [3]), INTERFACE_GPIO: ([2], [3])}
    data += LoggerData({INTERFACE_POWER: ([3], [4]),
                        INTERFACE_GPIO: ([1], [2])})
    assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3), (3, 4))
    assert tuple(data[INTERFACE_GPIO]) == ((2, 3), (1, 2))
    assert tuple(data[4]) == ((3, 5), (4, 6))


def test__add__():
    """Tests for __add__ function."""
    # Simple addition of objects
    data1 = LoggerData({INTERFACE_POWER: ([1], [2])})
    data2 = LoggerData({INTERFACE_POWER: ([2], [3])})
    data = data1 + data2
    assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3))
    # Check that data has been deep copied
    data1[INTERFACE_POWER] = ([4], [5])
    assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3))
    # Delete original copies (decrease reference count to them)
    del data1
    del data2
    assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3))
    # # Check that data has been shallow copied
    # data = LoggerData({INTERFACE_POWER: ([1], [2])}), "Incorrect value"
    # data1 = data
    # del data
    # assert data1[INTERFACE_POWER] == ((1, 2),), "Incorrect value"
    # Check that data has been deep copied
    data = LoggerData({INTERFACE_POWER: ([1], [2])})
    data1 = data + {}
    del data
    assert tuple(data1[INTERFACE_POWER]) == ((1, 2),)


def test_extend():
    """Tests for extend function."""
    # Simple extention of objects
    data = LoggerData({INTERFACE_POWER: ([1], [2])})
    data1 = InterfaceData([[2], [3]])
    data.extend(INTERFACE_POWER, data1)
    assert tuple(data[INTERFACE_POWER]) == ((1, 2), (2, 3))


def test_length():
    """Tests for length function."""
    data = LoggerData({
        INTERFACE_POWER: ([1], [2]),
        INTERFACE_GPIO: ([], []),
        4: ([3, 4], [5, 6])})
    # Length of individual interfaces
    assert data.length(INTERFACE_POWER) == 1
    assert data.length(INTERFACE_GPIO) == 0
    assert data.length(4) == 2

    # Lengths in dict of interfaces
    len_dict = data.length()
    assert len_dict[INTERFACE_POWER] == 1
    assert len_dict[INTERFACE_GPIO] == 0
    assert len_dict[4] == 2
