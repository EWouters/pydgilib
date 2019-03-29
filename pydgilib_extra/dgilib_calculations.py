
"""This module holds the functions that do calculations on Interface Data."""

import warnings

from pydgilib_extra.dgilib_extra_config import NUM_PINS


class StreamingCalculation(object):
    def __init__(self):
        self.data = []
        self.index = 0


class GPIOAugmentEdges(StreamingCalculation):
    """GPIO Augment Edges."""

    def gpio_augment_edges(self, gpio_data, delay_time=0, switch_time=0):
        """GPIO Augment Edges (streaming).

        Augments the edges of the GPIO data by inserting an extra sample of the
        previous pin values at moment before a switch occurs (minus switch_time
        ).
        The switch time is measured to be around 0.3 ms.

        Also delays all time stamps by delay_time. The delay time seems to vary
        a lot between different projects and should be manually specified for
        the best accuracy.

        Can insert the last datapoint again at the time specified (has to be
        after last sample).

        :param gpio_data: InterfaceData object of GPIO data.
        :type gpio_data: InterfaceData
        :param delay_time: Switch time of GPIO pin.
        :type delay_time: float
        :param switch_time: Switch time of GPIO pin.
        :type switch_time: float
        :return: InterfaceData object of augmented GPIO data.
        :rtype: InterfaceData
        """
        if not len(self.data):
            self.data = [True] * NUM_PINS
        pin_states = self.data

        # iterate over the list and insert items at the same time:
        i = 0
        while i < len(gpio_data):
            #print(gpio_data.timestamps[i], gpio_data.values[i])
            if gpio_data.values[i] != pin_states:
                # This inserts a time sample at time + switch time (so moves
                # the time stamp into the future)
                gpio_data.timestamps.insert(
                    i, gpio_data.timestamps[i] - switch_time)
                # This inserts the last datapoint again at the time the next
                # switch actually arrived (without switch time)
                gpio_data.values.insert(i, pin_states)
                i += 1
                pin_states = gpio_data.values[i]
            i += 1

        self.data = pin_states

        # Delay all time stamps by delay_time
        gpio_data.timestamps = [
            t + delay_time for t in gpio_data.timestamps]

        return gpio_data


def power_and_time_per_pulse(
        logger_data, pin, start_time=0.01, end_time=float("Inf"),
        stop_function=None, initialized=False, pulse_direction=True):
    """Calculate power and time per pulse.

    Takes the data and a pin and returns a list of power and time sums for
    each pulse of the specified pin.

    NOTE: This returns time durations in the sampling frame of the power
    timestamps. Hence the list of times this function returns will not exactly
    match with the difference between rise timestamp and fall timestamp of the
    of the GPIO pin.

    :param data: LoggerData object. Needs to have GPIO and Power data.
    :type data: LoggerData
    :param pin: Number of the GPIO pin to be used.
    :type pin: int
    :param start_time: First timestamp to consider (defaults to 0.01 to skip
        GPIO initialization).
    :type start_time: float
    :param end_time: Last timestamp to consider.
    :type end_time: float
    :param stop_function: Function to evaluate on `pin_values`. If it returns
        True the loop will stop.
    :type stop_function: function
    :param initialized: If False: Skip first occurrences of all pins high
    :type initialized: bool
    :param pulse_direction: If True: detect pulse as False -> True -> False,
        else detect pulse as True -> False -> True
    :type pulse_direction: bool
    :return: List of list of power and time sums.
    :rtype: tuple(list(float), list(float))
    """
    pin_value = False

    pulse_start_time = 0
    pulse_end_time = 0

    charges = []
    times = []

    power_index = 0

    # Loop over all gpio samples
    for timestamp, pin_values in logger_data.gpio:
        # Skip all samples until initialization has finished
        if not initialized:
            if all(pin_values):
                continue
            else:
                initialized = True
        if stop_function is not None and stop_function(pin_values):
            break
        # Detect inside start and end time
        if timestamp > start_time and timestamp <= end_time:
            # Detect rising edge (if pulse_direction else falling edge)
            if not pin_value and (pin_values[pin] ^ (not pulse_direction)):
                pin_value = pulse_direction
                pulse_start_time = timestamp
            # Detect falling edge (if pulse_direction else rising edge)
            if pin_value and (pin_values[pin] ^ pulse_direction):
                pin_value = False
                pulse_end_time = timestamp

                # Get the index of the power sample corresponding to the
                # rising edge
                power_index = start_index = logger_data.power.get_index(
                    pulse_start_time, power_index)
                # Get the index of the power sample corresponding to the
                # falling edge
                power_index = end_index = logger_data.power.get_index(
                    pulse_end_time, power_index)
                # Make sure the start index is larger than 0
                if start_index < 1:
                    start_index = 1
                    warnings.warn(
                        "Corrected a start_index of 0 in " +
                        "power_and_time_per_pulse.")

                # Sum charges and append to charges array
                charges.append(sum(logger_data.power.values[i] *
                                   (logger_data.power.timestamps[i] -
                                    logger_data.power.timestamps[i-1])
                                   for i in range(start_index, end_index)))
                times.append(logger_data.power.timestamps[end_index] -
                             logger_data.power.timestamps[start_index])

                # TODO: Check for off-by-one errors using a pytest testcases

    return charges, times


def rise_and_fall_times(
        logger_data, pin, start_time=0.01, end_time=float("Inf"),
        stop_function=None, initialized=False, pulse_direction=True):
    """rise_and_fall_times.

    [description]

    Arguments:
        logger_data {[type]} -- [description]
        pin {[type]} -- [description]

    Keyword Arguments:
        start_time {float} -- [description] (default: {0.01})
        end_time {[type]} -- [description] (default: {float("Inf")})
        stop_function {[type]} -- [description] (default: {None})
        initialized {bool} -- [description] (default: {False})
        pulse_direction {bool} -- [description] (default: {True})

    Returns:
        [type] -- [description]
    """
    pin_value = False

    rise_times = []
    fall_times = []

    # Loop over all gpio samples
    for timestamp, pin_values in logger_data.gpio:
        # Skip all samples until initialization has finished
        if not initialized:
            if all(pin_values):
                continue
            else:
                initialized = True
        if stop_function is not None and stop_function(pin_values):
            break
        # Detect inside start and end time
        if timestamp > start_time and timestamp <= end_time:
            # Detect rising edge (if pulse_direction else falling edge)
            if not pin_value and (pin_values[pin] ^ (not pulse_direction)):
                pin_value = pulse_direction
                rise_times.append(timestamp)
            # Detect falling edge (if pulse_direction else rising edge)
            if pin_value and (pin_values[pin] ^ pulse_direction):
                pin_value = False
                fall_times.append(timestamp)

    return rise_times, fall_times


def calculate_average(power_data, start_time=None, end_time=None,
                      start_index=1):
    """Calculate average value of the power_data using the left Riemann sum.

    Arguments:
        power_data {InterfaceData} -- Instance of InterfaceData with power
            samples.

    Keyword Arguments:
        start_time {float} -- Timestamp of first sample to include (default:
            {None})
        end_time {float} -- Timestamp to of last sample to include (default:
            {None})
        start_index {int} -- Index to start search for start time at (default:
            {1})

    Returns:
        [type] -- [description]
    """
    if start_time is None:
        start_index = 1
    else:
        start_index = power_data.get_index(start_time, start_index)
    if end_time is None:
        end_index = len(power_data) - 1
    else:
        end_index = power_data.get_index(end_time, start_index)

    # Make sure the start index is larger than 0
    if start_index < 1:
        start_index = 1
        warnings.warn(
            "Corrected a start_index of 0 in calculate_average.")

    return (sum(power_data.values[i] * (power_data.timestamps[i] -
                                        power_data.timestamps[i - 1])
                for i in range(start_index, end_index)) /
            (power_data.timestamps[end_index] -
             power_data.timestamps[start_index]))
