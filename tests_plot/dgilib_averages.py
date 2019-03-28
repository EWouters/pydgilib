from pydgilib_extra.dgilib_calculations import (
    calculate_average, StreamingCalculation, power_and_time_per_pulse,
    rise_and_fall_times)
from time import time

ITERATION = 0
HOLD_TIME = 1
HOLD_TIME_FROM = 0
HOLD_TIME_TO = 1
START_INDEX = 2
AVERAGE = 3


class DGILibAverages(object):

    def __init__(self, data=None, preprocessed_data=None, *args, **kwargs):
        self.data = data

        self.average_function = kwargs.get("average_function", "leftpoint")

        if preprocessed_data is None:
            self.hold_times_obj = HoldTimes()
            self.averages = [[], [], [], []]
            self.initialized = False
        else:
            self.averages = preprocessed_data
            self.initialized = True

        self.total_average = [0, 0, 0, 0]
        self.total_duration = [0, 0, 0, 0]
        self.total_iterations = [0, 0, 0, 0]
        self.benchmark_time = 0.0
        self.voltage = kwargs.get("voltage", 5)

    def read_from_csv(self, filepath, verbose=0):
        with open(filepath, "r") as f:
            for line in f:

                line_split = line.split(",")

                pin_idx = int(line_split[0])
                iteration = int(line_split[1])
                hold_time_from = float(line_split[2])
                hold_time_to = float(line_split[3])
                if "None" not in line_split[4]:
                    average = float(line_split[4])
                else:
                    average = None

                self.averages[pin_idx].append(
                    (iteration, (hold_time_from, hold_time_to), 0, average))

        self.initialized = True

        if verbose > 0:
            print("Read averages from CSV file:" + filepath)

    def write_to_csv(self, filepath, verbose=0):
        with open(filepath, "w") as f:
            for pin_idx in range(4):
                for i in range(len(self.averages[pin_idx])):
                    iteration = self.averages[pin_idx][i][ITERATION]
                    hold_time_from = self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_FROM]
                    hold_time_to = self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_TO]
                    #seconds = self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_TO] - self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_FROM]
                    average = self.averages[pin_idx][i][AVERAGE]

                    # if not(average is None):
                    f.write("{0},{1},{2},{3},{4}\n".format(
                        pin_idx, iteration, hold_time_from, hold_time_to, average))

            if verbose > 0:
                print("Wrote averages to: " + filepath)

    def print_averages_for_pin(self, pin_idx, how_many=9999):

        if len(self.averages) == 0:
            print("ERROR: Average information missing for all pins")
            return

        if len(self.averages[pin_idx]) == 0:
            print(
                "ERROR: No average data obtained for pin {0}".format(pin_idx))
            return

        for i in range(len(self.averages[pin_idx])):
            iteration_idx = self.averages[pin_idx][i][ITERATION]
            hold_times_0 = round(
                self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_FROM], 5)
            hold_times_1 = round(
                self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_TO], 5)

            if self.averages[pin_idx][i][AVERAGE] is not None:
                average = round(self.averages[pin_idx][i][AVERAGE] * 1000, 6)
            else:
                average = "ignored"

            # '{message:{fill}{align}{width}}'.format(
            #     message='Hi',
            #     fill=' ',
            #     align='<',
            #     width=16,
            # )
            interval_duration = round(hold_times_1 - hold_times_0, 5)

            if (i < how_many):
                print("{0: >5}: ({1: >10} s, {2: >10} s) = {3: >10} s {4: >15} mC".format(
                    iteration_idx,
                    hold_times_0,
                    hold_times_1,
                    interval_duration,
                    average))

        if (self.total_iterations[pin_idx] > 0):

            print("Average charge per iteration: {0} uC".format(round(
                self.total_average[pin_idx] * 1000 * 1000 / self.total_iterations[pin_idx], 9)))
            print("Average energy per iteration: {0} uJ".format(round(
                self.total_average[pin_idx]*self.voltage * 1000 * 1000 / self.total_iterations[pin_idx], 6)))
            print("Average time per iteration: {0} ms".format(
                round(self.total_duration[pin_idx] / self.total_iterations[pin_idx], 6)))
            print("")
            print("Total iterations: {0}".format(
                self.total_iterations[pin_idx]))
            print("Total average current: {0} mA".format(
                round(self.total_average[pin_idx] * 1000 / self.total_duration[pin_idx], 6)))
            print("Total charge: {0} mC".format(
                round(self.total_average[pin_idx] * 1000, 6)))
            print("Total energy: {0} mJ".format(
                round(self.total_average[pin_idx]*self.voltage * 1000, 6)))
            print("Total time: {0} s".format(
                round(self.total_duration[pin_idx], 6)))
            print("")
            print("Benchmark time: {0} s".format(
                round(self.benchmark_time, 8)))
        else:
            print(
                "Averages not calculated or no average data for pin {0}.".format(pin_idx))

    def calculate_averages_for_pin(self, pin_idx, pin_value=True, ignore_first_average=True):
        start_time = time()

        if self.average_function == "leftpoint":
            start_index = 1

            if not self.initialized:
                hold_times_all = self.hold_times_obj.identify_hold_times(
                    pin_idx, pin_value, self.data.gpio)
                self.averages = [[], [], [], []]
                if hold_times_all is not None:
                    self.averages[pin_idx] = [
                        (None, (None, None), None, None)] * len(hold_times_all)
                else:
                    self.averages[pin_idx] = []

            for i in range(len(self.averages[pin_idx])):

                if self.initialized:
                    iteration_idx = self.averages[pin_idx][i][ITERATION]
                    hold_times = self.averages[pin_idx][i][HOLD_TIME]
                    start_index = max(
                        start_index, self.averages[pin_idx][i][START_INDEX])
                    average = self.averages[pin_idx][i][AVERAGE]
                else:
                    iteration_idx = i+1
                    hold_times = hold_times_all[i]

                    average = None

                if ignore_first_average and iteration_idx == 1:
                    average = None
                elif average is None:
                    average, start_index = calculate_average_leftpoint_single_interval(
                        self.data.power, hold_times[0], hold_times[1], start_index)

                if average is not None:
                    self.total_average[pin_idx] += average
                    self.total_duration[pin_idx] += hold_times[1] - \
                        hold_times[0]
                    self.total_iterations[pin_idx] += 1
                else:
                    average = None
                self.averages[pin_idx][i] = (
                    iteration_idx, hold_times, start_index, average)
        else:
            charges, times = power_and_time_per_pulse(self.data, pin_idx)
            hold_times = rise_and_fall_times(self.data, pin_idx)

            start_from = 0
            if ignore_first_average:
                start_from = 1

            for i in range(start_from, len(charges)):
                self.total_average[pin_idx] += charges[i]
                self.total_iterations[pin_idx] += 1
                if i >= len(self.averages[pin_idx]):
                    self.averages[pin_idx].append(
                        (i, (hold_times[0][i], hold_times[1][i]), 0, charges[i]))
                else:
                    self.averages[pin_idx][i] = (
                        i, (hold_times[0][i], hold_times[1][i]), 0, charges[i])
                self.total_duration[pin_idx] += times[i]

        end_time = time()
        self.benchmark_time = end_time - start_time


##############################
# Identify toggle/hold times #
##############################


def what_value_is_at_time_t_for_pin(data, pin, t):
    index_of_timestamp = data.gpio.timestamps.index(t)
    return data.gpio.values[index_of_timestamp]


class HoldTimes(StreamingCalculation):

    def identify_toggle_times(self, pin, data_gpio=None, gpio_start_index=0):
        if data_gpio is None:
            data_gpio = self.data
        if gpio_start_index == None:
            gpio_start_index = self.index

        if len(data_gpio.timestamps) <= 1:
            return []  # We can't identify intervals with only one value
        if gpio_start_index > (len(data_gpio.timestamps) - 1):
            return []  # We're being asked to do an index that does not exist yet, so just skip

        toggle_times = []
        true_to_false_toggle_times = []
        false_to_true_toggle_times = []

        #last_toggle_timestamp = data_gpio.timestamps[start_index]
        last_toggle_value = data_gpio.values[gpio_start_index][pin]

        #print("New data, starting on pin " + str(pin) + " at timestamp " + str(data_gpio.timestamps[start_index]) + " of value " + str(last_toggle_value) + ". Index is: " + str(start_index))

        for i in range(gpio_start_index, len(data_gpio)):
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
        if len(data_gpio.timestamps) <= 1:
            return []  # We can't identify intervals with only one value
        if self.index > (len(data_gpio.timestamps) - 1):
            return []  # We're being asked to do an index that does not exist yet, so just skip

        hold_times = []

        (_, true_to_false_times, false_to_true_times) = self.identify_toggle_times(
            pin, data_gpio, self.index)

        #print("T2F: " + str(true_to_false_times))
        #print("F2T: " + str(false_to_true_times))

        if len(false_to_true_times) == 0:
            return
        if len(true_to_false_times) == 0:
            return

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

        hold_times_list = list(hold_times)

        try:
            self.index = data_gpio.timestamps.index(
                hold_times_list[-1][-1]) + 1
        except IndexError:
            # If you remove this, you get an error
            pass

        return hold_times_list

###############################
# Calculate average leftpoint #
###############################


def calculate_average_multiple_intervals(data_power, intervals, start_time=None, end_time=None):
    sum = 0
    to_divide = 0

    for intv in intervals:
        if ((intv[0] >= start_time) and (intv[0] <= end_time) and (intv[1] >= start_time) and (intv[1] <= end_time)):
            sum += calculate_average(data_power, intv[0], intv[1], -1)
            to_divide += 1

    return sum / to_divide


def calculate_average_leftpoint_single_interval(data_power, start_time=None, end_time=None, power_start_index=0):

    # Get the timestamps nearest to 'timestamp_to_compare' in the power data.
    #  Usually the 'timestamp_to_compare' is a timestamp from gpio data, and this
    #  function is getting the left/right timestamps from the power data
    def get_nearest_timestamps(data_power, timestamp_to_compare, start_index=0):
        index = data_power.get_index(timestamp_to_compare, start_index)

        if data_power.timestamps[index] >= timestamp_to_compare:
            if index == 0:
                return (None, data_power.timestamps[index], None, index)
            else:
                return (data_power.timestamps[index-1], data_power.timestamps[index], index-1, index)
        else:
            return (None, None, None, None)

    #beginning_time = time()
    if start_time is None:
        start_time = data_power.timestamps[0]
    else:
        (_, start_time, _, left_index) = get_nearest_timestamps(
            data_power, start_time, power_start_index)
    #duration = time() - beginning_time
    #print("[calculate_average_leftpoint_single_interval benchmark] Start time get: {0} s with index {1}".format(duration, power_start_index))

    #beginning_time = time()
    if end_time is None:
        end_time = data_power.timestamps[-1]
    else:
        (end_time, _, right_index, _) = get_nearest_timestamps(
            data_power, end_time, left_index)

    if start_time is None:
        return None
    if end_time is None:
        return None
    if left_index is None:
        return None
    if right_index is None:
        return None

    last_time = start_time

    sum = 0

    #beginning_time = time()
    for i in range(left_index, right_index+1):  # +1 to include right_index
        timestamp = data_power.timestamps[i]
        power_value = data_power.values[i]

        sum += power_value * (timestamp - last_time)
        last_time = timestamp
    #duration = time() - beginning_time
    #print("[calculate_average_leftpoint_single_interval benchmark] Main for loop: {0} s".format(duration))

    return sum, right_index  # / (end_time - start_time)
