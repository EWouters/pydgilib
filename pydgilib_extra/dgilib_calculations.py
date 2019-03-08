
"""This module holds the functions that do calculations on Interface Data."""


from pydgilib_extra.dgilib_extra_config import NUM_PINS


class StreamingCalculation(object):
    def __init__(self):
        self.data = []
        self.index = 0


class HoldTimes(StreamingCalculation):
    def get_hold_times(self, gpio_data):
        """Calculate new hold times for data after get_hold_times.index"""
        self.data += gpio_data.timestamps  # TODO
        self.index = len(gpio_data)
        print("Calculate and return hold times")
        return self.data


def gpio_augment_edges(
        gpio_data, delay_time=0, switch_time=0, extend_to=None):
    """GPIO Augment Edges.

    Augments the edges of the GPIO data by inserting an extra sample of the
    previous pin values at moment before a switch occurs (minus switch_time).
    The switch time is measured to be around 0.3 ms.

    Also delays all time stamps by delay_time. The delay time seems to vary
    a lot between different projects and should be manually specified for the
    best accuracy.

    Can insert the last datapoint again at the time specified (has to be after
    last sample).

    :param gpio_data: InterfaceData object of GPIO data.
    :type gpio_data: InterfaceData
    :param delay_time: Switch time of GPIO pin.
    :type delay_time: float
    :param switch_time: Switch time of GPIO pin.
    :type switch_time: float
    :param extend_to: Inserts the last pin values again at the time specified
        (only used if time is after last sample).
    :type extend_to: float
    :return: InterfaceData object of augmented GPIO data.
    :rtype: InterfaceData
    """
    pin_states = [False] * NUM_PINS

    # iterate over the list and insert items at the same time:
    i = 0
    while i < len(gpio_data.timestamps):
        if gpio_data.values[i] != pin_states:
            # This inserts a time sample at time + switch time (so moves the
            # time stamp into the future)
            gpio_data.timestamps.insert(
                i, gpio_data.timestamps[i] - switch_time)
            # This inserts the last datapoint again at the time the next
            # switch actually arrived (without switch time)
            gpio_data.values.insert(i, pin_states)
            i += 1
            pin_states = gpio_data.values[i]
        i += 1

    # Delay all time stamps by delay_time
    gpio_data.timestamps = [
        t + delay_time for t in gpio_data.timestamps]

    if extend_to is not None:
        if extend_to >= gpio_data.timestamps[-1]:
            gpio_data.timestamps.append(extend_to)
            gpio_data.values.append(pin_states)
    return gpio_data
