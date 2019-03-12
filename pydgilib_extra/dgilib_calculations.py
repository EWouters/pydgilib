
"""This module holds the functions that do calculations on Interface Data."""

import warnings

from pydgilib_extra.dgilib_extra_config import NUM_PINS

###############################
# Streaming Calculation Class #
###############################
class StreamingCalculation(object):
    def __init__(self):
        self.data = []
        self.index = 0

#################################################
# GPIO Augment Edges + Power and time per pulse #
#################################################
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
            self.data = [False] * NUM_PINS
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


# def gpio_augment_edges(gpio_data, delay_time=0, switch_time=0, extend_to=None):
#     """GPIO Augment Edges (standalone).

#     Augments the edges of the GPIO data by inserting an extra sample of the
#     previous pin values at moment before a switch occurs (minus switch_time).
#     The switch time is measured to be around 0.3 ms.

#     Also delays all time stamps by delay_time. The delay time seems to vary
#     a lot between different projects and should be manually specified for the
#     best accuracy.

#     Can insert the last datapoint again at the time specified (has to be after
#     last sample).

#     :param gpio_data: InterfaceData object of GPIO data.
#     :type gpio_data: InterfaceData
#     :param delay_time: Switch time of GPIO pin.
#     :type delay_time: float
#     :param switch_time: Switch time of GPIO pin.
#     :type switch_time: float
#     :param extend_to: Inserts the last pin values again at the time specified
#         (only used if time is after last sample).
#     :type extend_to: float
#     :return: InterfaceData object of augmented GPIO data.
#     :rtype: InterfaceData
#     """
#     pin_states = [False] * NUM_PINS

#     # iterate over the list and insert items at the same time:
#     i = 0
#     while i < len(gpio_data.timestamps):
#         if gpio_data.values[i] != pin_states:
#             # This inserts a time sample at time + switch time (so moves the
#             # time stamp into the future)
#             gpio_data.timestamps.insert(
#                 i, gpio_data.timestamps[i] - switch_time)
#             # This inserts the last datapoint again at the time the next
#             # switch actually arrived (without switch time)
#             gpio_data.values.insert(i, pin_states)
#             i += 1
#             pin_states = gpio_data.values[i]
#         i += 1

#     # Delay all time stamps by delay_time
#     gpio_data.timestamps = [
#         t + delay_time for t in gpio_data.timestamps]

#     if extend_to is not None:
#         if extend_to >= gpio_data.timestamps[-1]:
#             gpio_data.timestamps.append(extend_to)
#             gpio_data.values.append(pin_states)
#     return gpio_data


def power_and_time_per_pulse(logger_data, pin, start_time=None, end_time=None,
                             pulse_direction=True):
    """Calculate power and time per pulse.

    Takes the data and a pin and returns a list of power and time sums for
    each pulse of the specified pin.

    :param data: LoggerData object. Needs to have GPIO and Power data.
    :type data: LoggerData
    :param pin: Number of the GPIO pin to be used.
    :type pin: int
    :param start_time: First timestamp to consider.
    :type start_time: float
    :param end_time: Last timestamp to consider.
    :type end_time: float
    :param pulse_direction: If True: detect pulse as False -> True -> False,
        else detect pulse as True -> False -> True
    :type pulse_direction: bool
    :return: List of list of power and time sums.
    :rtype: tuple(list(float), list(float))
    """
    if start_time is None:
        start_time = 0
    if end_time is None:
        end_time = float("Inf")

    pin_value = not pulse_direction

    pulse_start_time = 0
    pulse_end_time = 0

    charges = []
    times = []

    power_index = 0

    # Loop over all gpio samples
    for timestamp, pin_values in logger_data.gpio:
        # Detect inside start and end time
        if timestamp > start_time and timestamp <= end_time:
            # Detect rising edge
            if not pin_value and pin_values[pin]:
                pin_value = pulse_direction
                pulse_start_time = timestamp
            # Detect falling edge
            if pin_value and not pin_values[pin]:
                pin_value = not pulse_direction
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

##############################
# Identify toggle/hold times #
##############################

def what_value_is_at_time_t_for_pin(data, pin, t):
    index_of_timestamp = data.gpio.timestamps.index(t)
    return data.gpio.values[index_of_timestamp]

class HoldTimes(StreamingCalculation):

    def __init__(self):
        StreamingCalculation.__init__(self)

    def identify_toggle_times(self, pin, data_gpio=None, start_index=None):
        if data_gpio is None:
            data_gpio = self.data
        if start_index == None:
             start_index = self.index

        if len(data_gpio.timestamps) <= 1:
            return []  # We can't identify intervals with only one value
        if start_index > (len(data_gpio.timestamps) - 1):
            return []  # We're being asked to do an index that does not exist yet, so just skip

        toggle_times = []
        true_to_false_toggle_times = []
        false_to_true_toggle_times = []

        #last_toggle_timestamp = data_gpio.timestamps[start_index]
        last_toggle_value = data_gpio.values[start_index][pin]

        #print("New data, starting on pin " + str(pin) + " at timestamp " + str(data_gpio.timestamps[start_index]) + " of value " + str(last_toggle_value) + ". Index is: " + str(start_index))

        for i in range(start_index, len(data_gpio)):
            if last_toggle_value != data_gpio.values[i][pin]:
                #print("Detected toggle on pin " + str(pin) + " at timestamp " + str(data_gpio.timestamps[i]) + " of value " + str(data_gpio.values[i][pin]) + ". Index is: " + str(i))
                toggle_times.append(data_gpio.timestamps[i])
                if last_toggle_value == True:
                    true_to_false_toggle_times.append(data_gpio.timestamps[i])
                if last_toggle_value == False:
                    false_to_true_toggle_times.append(data_gpio.timestamps[i])

                #last_toggle_timestamp = data_gpio.timestamps[i]
                last_toggle_value = data_gpio.values[i][pin]

        # A smart printing for debugging this function
        # Either leave 'debug = False' or comment it, but don't lose it
        debug = False
        if debug:
            for (t, v) in data_gpio:
                # print(str((t,v)))
                if t in toggle_times:
                    print("\t" + str(t) + "\t\t" + str(v) + "\t <-- toggled")
                else:
                    print("\t" + str(t) + "\t\t" + str(v))

        # , last_toggle_index
        return toggle_times, true_to_false_toggle_times, false_to_true_toggle_times

    def identify_hold_times(self, pin, pin_value, data_gpio=None):
        if data_gpio is None:
            data_gpio = self.data
        else:
            self.data = data_gpio
        if len(data_gpio.timestamps) <= 1:
            return []  # We can't identify intervals with only one value
        if self.index > (len(data_gpio.timestamps) - 1):
            return []  # We're being asked to do an index that does not exist yet, so just skip

        hold_times = []

        (_, true_to_false_times, false_to_true_times) = self.identify_toggle_times(pin, data_gpio, self.index)

        #print("T2F: " + str(true_to_false_times))
        #print("F2T: " + str(false_to_true_times))

        if len(false_to_true_times) == 0: return
        if len(true_to_false_times) == 0: return

        if (pin_value == True):
            # A fix
            if false_to_true_times[0] > true_to_false_times[0]:
                true_to_false_times.pop(0)
            hold_times = zip(false_to_true_times, true_to_false_times)
        elif (pin_value == False):
            # A fix
            if true_to_false_times[0] > false_to_true_times[0]:
                false_to_true_times.pop(0)
            hold_times = zip(true_to_false_times, false_to_true_times)         

        # A smart printing for debugging this function
        # Either leave 'debug = False' or comment it, but don't lose it
        debug = False
        if debug:
            ht_zip = list(zip(*hold_times))
            for (t, v) in data_gpio:
                # print(str((t,v)))
                if t in ht_zip[0]:
                    print("\t" + str(t) + "\t\t" + str(v) + "\t <-- start")
                elif t in ht_zip[1]:
                    print("\t" + str(t) + "\t\t" + str(v) + "\t <-- stop")
                else:
                    print("\t" + str(t) + "\t\t" + str(v))

        hold_times_l = list(hold_times)
        
        try:
            self.index = data_gpio.timestamps.index(hold_times_l[-1][-1]) + 1
        except IndexError:
            # If you remove this, you get an error
            pass

        #print(str(hold_times_l))
        return hold_times_l

###############################
# Calculate average leftpoint #
###############################

def calculate_average_leftpoint_single_interval(data_power, start_time=None, end_time=None, start_index=0):
    """Calculate average value of the power_data using the left Riemann sum."""
    # print("Start time: " + str(start_time))
    # print("End time: " + str(end_time))
    # print("Timestamps: " + str(data_power.timestamps))
    if start_time is None:
        start_time = data_power.timestamps[0]
    else:
        (_, start_time, _, left_index) = data_power.get_next_available_timestamps(start_time, start_index)
 

    if end_time is None:
        end_time = data_power.timestamps[-1]
    else:
        (end_time, _, right_index, _) = data_power.get_next_available_timestamps(end_time, start_index)

    if start_time is None: return None
    if end_time is None: return None
    if left_index is None: return None
    if right_index is None: return None

    last_time = start_time

    sum = 0

    for i in range(left_index, right_index+1):
        timestamp = data_power.timestamps[i]
        power_value = data_power.values[i]

        sum += power_value * (timestamp - last_time)
        last_time = timestamp
    
    return sum / (end_time - start_time)

def calculate_average_leftpoint_multiple_intervals(data_power, intervals, start_time=None, end_time=None):
    # Calculate average value using midpoint Riemann sum
    sum = 0
    to_divide = 0

    for intv in intervals:
        if ((intv[0] >= start_time) and (intv[0] <= end_time) and (intv[1] >= start_time) and (intv[1] <= end_time)):
            sum += calculate_average_leftpoint_single_interval( 
                data_power, intv[0], intv[1])
            to_divide += 1

    return sum / to_divide

##############################
# Calculate average midpoint #
##############################

def calculate_average_midpoint_single_interval(power_data, start_time=None, end_time=None):
    # Calculate average value using midpoint Riemann sum
    sum = 0

    actual_start_time = -1
    actual_end_time = -1

    for i in range(len(power_data[0]) - 1)[1:]:
        first_current_value = power_data[1][i]
        second_current_value = power_data[1][i + 1]
        timestamp = power_data[0][i + 1]
        last_time = power_data[0][i]

        if ((last_time >= start_time) and (last_time < end_time)):
            sum += ((first_current_value + second_current_value) / 2) * \
                (timestamp - last_time)

            # We have to select the actual start time and the actual
            if (actual_start_time == -1):
                actual_start_time = power_data[0][i]

        if (timestamp >= end_time):
            actual_end_time = power_data[0][i - 1]
            break

    return sum / (actual_end_time - actual_start_time)


def calculate_average_midpoint_multiple_intervals(power_data, intervals, start_time=None, end_time=None):
    # Calculate average value using midpoint Riemann sum
    sum = 0
    to_divide = 0

    for intv in intervals:
        if ((intv[0] >= start_time) and (intv[0] <= end_time) and (intv[1] >= start_time) and (intv[1] <= end_time)):
            sum += calculate_average_midpoint_single_interval(
                power_data, intv[0], intv[1])
            to_divide += 1

    return sum / to_divide

##########################################
# Obsolete / Possibly obsolete functions #
##########################################
# def power_filter_by_pin(pin, data, verbose=0):
#     """Filter the data to when a specified pin is high."""
#     power_data = copy.deepcopy(data[INTERFACE_POWER])

#     pin_value = False

#     power_index = 0

#     if verbose:
#         print(
#             f"power_filter_by_pin filtering  {len(power_data[0])} power "
#             f"samples.")

#     for timestamp, pin_values in zip(*data[INTERFACE_GPIO]):
#         while (power_index < len(power_data[0]) and
#                power_data[0][power_index] < timestamp):
#             power_data[1][power_index] *= pin_value
#             power_index += 1

#         if pin_values[pin] != pin_value:
#             if verbose:
#                 print(f"\tpin {pin} changed at {timestamp}, {pin_value}")
#             pin_value = pin_values[pin]

#     return power_data
