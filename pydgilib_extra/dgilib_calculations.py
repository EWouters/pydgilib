
"""This module holds the functions that do calculations on Interface Data."""


from pydgilib_extra.dgilib_extra_config import NUM_PINS

#####################
# Streaming Classes #
#####################
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

#################################################
# GPIO Augment Edges + Power and time per pulse #
#################################################

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

def power_and_time_per_pulse(data, pin, verbose=0, power_factor=1e3):
    """Calculate power and time per pulse.

    Takes the data and a pin and returns a list of power and time sums for
    each pulse of the specified pin. It stops when all pins are high.

    :param data: Data structure holding the samples.
    :type data: dict(256:list(list(float), list(float)), 48:list(list(float),
        list(list(bool))))
    :param pin: Number of the pin to be used.
    :type pin: int
    :return: List of list of power and time sums.
    :rtype: tuple(list(float), list(float))
    """
    pin_value = False

    charges = []
    times = []

    power_index = 0
    power_sum = 0
    time_sum = 0

    start_time = 0
    end_time = 0
    last_time = 0

    for timestamp, pin_values in zip(*data[INTERFACE_GPIO]):
        if all(pin_values):
            if verbose:
                print(
                    f"power_and_time_per_pulse done, charges: {len(charges)}, "
                    f"times: {len(times)}")
            break
        if not pin_value and pin_values[pin]:
            pin_value = True
            start_time = timestamp
            last_time = timestamp
        if pin_value and not pin_values[pin]:
            pin_value = False
            end_time = timestamp
            while (power_index < len(data[INTERFACE_POWER][0]) and
                   data[INTERFACE_POWER][0][power_index] <= end_time):
                if (data[INTERFACE_POWER][0][power_index] >= start_time):
                    power_sum += data[INTERFACE_POWER][1][power_index] * \
                        (data[INTERFACE_POWER][0][power_index] - last_time)
                    time_sum += (data[INTERFACE_POWER][0]
                                 [power_index] - last_time)
                last_time = data[INTERFACE_POWER][0][power_index]
                power_index += 1

            charges.append(power_sum*power_factor)
            times.append(time_sum)
            power_sum = 0
            time_sum = 0

    return charges, times

##############################
# Identify toggle/hold times #
##############################

def what_value_is_at_time_t_for_pin(data, pin, t):
    index_of_timestamp = data.gpio.timestamps.index(t)
    return data.gpio.values[index_of_timestamp]

def identify_toggle_times(data, pin, start_index=0):
    if len(data.gpio.timestamps) <= 1: return [] # We can't identify intervals with only one value
    if start_index > (len(data.gpio.timestamps) - 1): return [] # We're being asked to do an index that does not exist yet, so just skip

    toggle_times = []
    true_to_false_toggle_times = []
    false_to_true_toggle_times = []

    last_toggle_timestamp = data.gpio.timestamps[start_index]
    last_toggle_value = data.gpio.values[start_index][pin]

    for i in range(start_index+1, len(data.gpio)):
        if last_toggle_value != data.gpio.values[i][pin]:
            toggle_times.append(data.gpio.timestamps[i])
            if last_toggle_value == True:
                true_to_false_toggle_times.append(data.gpio.timestamps[i])
            if last_toggle_value == False:
                false_to_true_toggle_times.append(data.gpio.timestamps[i])

            last_toggle_timestamp = data.gpio.timestamps[i]
            last_toggle_value = data.gpio.values[i][pin]
    
    # A smart printing for debugging this function
    # Either leave 'debug = False' or comment it, but don't lose it
    debug = False
    if debug:
        for (t, v) in data.gpio:
            #print(str((t,v)))
            if t in toggle_times:
                print("\t" + str(t) + "\t\t" + str(v) + "\t <-- toggled")
            else:
                print("\t" + str(t) + "\t\t" + str(v))
    
    return toggle_times, true_to_false_toggle_times, false_to_true_toggle_times#, last_toggle_index

def identify_hold_times(data, pin, pin_value, start_index):
    if len(data.gpio.timestamps) <= 1: return [] # We can't identify intervals with only one value
    if start_index > (len(data.gpio.timestamps) - 1): return [] # We're being asked to do an index that does not exist yet, so just skip

    hold_times = []

    (_, true_to_false_times, false_to_true_times) = identify_toggle_times(data, pin, start_index)

    if (pin_value == True):
        hold_times = zip(false_to_true_times, true_to_false_times)
    elif (pin_value == False):
        hold_times = zip(true_to_false_times, false_to_true_times)
    
    # A smart printing for debugging this function
    # Either leave 'debug = False' or comment it, but don't lose it
    debug = False
    if debug:
        ht_zip = list(zip(*hold_times))
        for (t, v) in data.gpio:
            #print(str((t,v)))
            if t in ht_zip[0]:
                print("\t" + str(t) + "\t\t" + str(v) + "\t <-- start")
            elif t in ht_zip[1]:
                print("\t" + str(t) + "\t\t" + str(v) + "\t <-- stop")
            else:
                print("\t" + str(t) + "\t\t" + str(v))
    
    #print(str(hold_times))

    return list(hold_times)

###############################
# Calculate average leftpoint #
###############################

# TODO: To be included here?

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
            sum += ((first_current_value + second_current_value) / 2) * (timestamp - last_time)

            # We have to select the actual start time and the actual 
            if (actual_start_time == -1): actual_start_time = power_data[0][i]

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
            sum += calculate_average_midpoint_single_interval(power_data, intv[0], intv[1])
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