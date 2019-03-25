from pydgilib_extra.dgilib_calculations import calculate_average, calculate_average_leftpoint_single_interval, power_and_time_per_pulse, rise_and_fall_times, HoldTimes
from time import time

ITERATION = 0
HOLD_TIME = 1
HOLD_TIME_FROM = 0
HOLD_TIME_TO = 1
START_INDEX = 2
AVERAGE = 3

class DGILibAverages(object):

    def __init__(self, data = None, preprocessed_data = None, *args, **kwargs):
        self.data = data

        self.average_function = kwargs.get("average_function", "leftpoint") # Unused for now

        if preprocessed_data is None:
            self.hold_times_obj = HoldTimes() # TODO: Calculate yourself if we don't get preprocessed data from plot
            self.averages = [[],[],[],[]]
            self.initialized = False       
        else:
            self.averages = preprocessed_data
            self.initialized = True

        self.total_average = [0,0,0,0]
        self.total_duration = [0,0,0,0]
        self.total_iterations = [0,0,0,0]
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

                self.averages[pin_idx].append((iteration, (hold_time_from, hold_time_to), 0, average))

        self.initialized = True

        if verbose > 0: print("Read averages from CSV file:" + filepath)


    def write_to_csv(self, filepath, verbose=0):       
        with open(filepath, "w") as f:
            for pin_idx in range(4):
                for i in range(len(self.averages[pin_idx])):
                    iteration = self.averages[pin_idx][i][ITERATION]
                    hold_time_from = self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_FROM]
                    hold_time_to = self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_TO]
                    #seconds = self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_TO] - self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_FROM]
                    average = self.averages[pin_idx][i][AVERAGE]

                    #if not(average is None):
                    f.write("{0},{1},{2},{3},{4}\n".format(pin_idx, iteration, hold_time_from, hold_time_to, average))

            if verbose > 0: print("Wrote averages to CSV file: "+ filepath)

    def print_averages_for_pin(self, pin_idx, how_many=9999):

        if len(self.averages) == 0:
            print("ERROR: Average information missing for all pins")
            return

        if len(self.averages[pin_idx]) == 0:
            print("ERROR: No average data obtained for pin {0}".format(pin_idx))
            return

        for i in range(len(self.averages[pin_idx])):
            iteration_idx = self.averages[pin_idx][i][ITERATION]
            hold_times_0 = round(self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_FROM], 5)
            hold_times_1 = round(self.averages[pin_idx][i][HOLD_TIME][HOLD_TIME_TO], 5)

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

            print("Average charge per iteration: {0} uC".format(round(self.total_average[pin_idx] * 1000 / self.total_iterations[pin_idx], 9)))
            print("Average energy per iteration: {0} uJ".format(round(self.total_average[pin_idx]*self.voltage*1000 / self.total_iterations[pin_idx], 6)))
            print("Average time per iteration: {0} ms".format(round(self.total_duration[pin_idx] / self.total_iterations[pin_idx], 6)))
            print("")
            print("Total iterations: {0}".format(self.total_iterations[pin_idx]))
            print("Total average current: {0} mA".format(round(self.total_average[pin_idx] * 1000 / self.total_duration[pin_idx], 6)))
            print("Total charge: {0} mC".format(round(self.total_average[pin_idx] * 1000, 6)))
            print("Total energy: {0} mJ".format(round(self.total_average[pin_idx]*self.voltage* 1000, 6)))
            print("Total time: {0} s".format(round(self.total_duration[pin_idx], 6)))
            print("")
            print("Benchmark time: {0} s".format(round(self.benchmark_time, 8)))
        else:
            print("Averages not calculated or no average data for pin {0}.".format(pin_idx))
        

    def calculate_averages_for_pin(self, pin_idx, pin_value = True, ignore_first_average = True):
        start_time = time()

        if self.average_function == "leftpoint":
            start_index = 1

            if not self.initialized:
                hold_times_all = self.hold_times_obj.identify_hold_times(pin_idx, pin_value, self.data.gpio)
                self.averages = [[],[],[],[]]
                if hold_times_all is not None:
                    self.averages[pin_idx] = [(None, (None, None), None, None)] * len(hold_times_all)
                else:
                    self.averages[pin_idx] = []
            
            for i in range(len(self.averages[pin_idx])):

                if self.initialized:
                    iteration_idx = self.averages[pin_idx][i][ITERATION]
                    hold_times = self.averages[pin_idx][i][HOLD_TIME]
                    start_index = max(start_index, self.averages[pin_idx][i][START_INDEX])
                    average = self.averages[pin_idx][i][AVERAGE]
                else:
                    iteration_idx = i+1
                    hold_times = hold_times_all[i]
                    start_index = 0
                    average = None

                if ignore_first_average and iteration_idx == 1:
                    average = None
                elif average is None:
                    average, start_index = calculate_average_leftpoint_single_interval(self.data.power, hold_times[0], hold_times[1], start_index)

                if average is not None:
                    self.total_average[pin_idx] += average
                    self.total_duration[pin_idx] += hold_times[1] - hold_times[0]
                    self.total_iterations[pin_idx] += 1
                else:
                    average = None
                self.averages[pin_idx][i] = (iteration_idx, hold_times, start_index, average)
        else:
            charges, times = power_and_time_per_pulse(self.data, pin_idx)
            hold_times = rise_and_fall_times(self.data, pin_idx)

            start_from = 0
            if ignore_first_average: start_from = 1

            for i in range(start_from, len(charges)):
                self.total_average[pin_idx] += charges[i]
                self.total_iterations[pin_idx] += 1
                if i >= len(self.averages[pin_idx]):
                    self.averages[pin_idx].append((i, (hold_times[0][i], hold_times[1][i]), 0, charges[i]))
                else:
                    self.averages[pin_idx][i] = (i, (hold_times[0][i], hold_times[1][i]), 0, charges[i])
                self.total_duration[pin_idx] += times[i]

        end_time = time()
        self.benchmark_time = end_time - start_time
