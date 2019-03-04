"""This module holds the benchmark tests for DGILibExtra."""

from pydgilib_extra import (LoggerData, INTERFACE_POWER, INTERFACE_GPIO)

num_iterations = 10000
num_values = 1000


def data_iadd_speed(num_iterations=10, num_values=1000):
    """test_data_iadd_speed."""
    data = LoggerData([INTERFACE_POWER, INTERFACE_GPIO])
    for _ in range(num_iterations):
        data += {
            INTERFACE_POWER: (list(range(num_values)), list(range(num_values))),
            INTERFACE_GPIO: (list(range(num_values)), list(range(num_values)))}
    return data


def test_data_iadd_speed(benchmark):
    """Benchmark iadd speed."""
    result = benchmark(data_iadd_speed, num_iterations, num_values)

    assert len(result[INTERFACE_POWER]) == num_iterations * num_values
    assert len(result[INTERFACE_GPIO]) == num_iterations * num_values


def data_no_class_speed(num_iterations=10, num_values=1000):
    """data_no_class_speed."""
    data = {INTERFACE_POWER: ([], []), INTERFACE_GPIO: ([], [])}
    for _ in range(num_iterations):
        data[INTERFACE_POWER][0].extend(list(range(num_values)))
        data[INTERFACE_POWER][1].extend(list(range(num_values)))
        data[INTERFACE_GPIO][0].extend(list(range(num_values)))
        data[INTERFACE_GPIO][1].extend(list(range(num_values)))
    return data


def test_data_no_class_speed(benchmark):
    """Benchmark no_class speed."""
    result = benchmark(data_no_class_speed, num_iterations, num_values)

    assert len(result[INTERFACE_POWER][0]) == num_iterations * num_values
    assert len(result[INTERFACE_POWER][1]) == num_iterations * num_values
    assert len(result[INTERFACE_GPIO][0]) == num_iterations * num_values
    assert len(result[INTERFACE_GPIO][1]) == num_iterations * num_values
