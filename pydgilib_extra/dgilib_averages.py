from pydgilib_extra.dgilib_calculations import HoldTimes
from pydgilib_extra.dgilib_calculations import calculate_average, calculate_average_leftpoint_single_interval

class DGILibAverages(object):

    def __init__(self, dgilib_extra, preprocessed_data = None, *args, **kwargs):
        self.dgilib_extra = dgilib_extra
        self.average_function = kwargs.get("average_function", "leftpoint") # Unused for now

        if preprocessed_data is None:
            self.hold_times_obj = HoldTimes() # TODO: Calculate yourself if we don't get preprocessed data from plot
            self.averages = [[],[],[],[]]
            raise NotImplementedError("Need to make DGILibAverages work by itself when the plot does not precalculate data")
        else:
            self.averages = preprocessed_data

        self.total_average = [0,0,0,0]
        self.total_duration = [0,0,0,0]
        self.total_iterations = [0,0,0,0]
        self.voltage = kwargs.get("voltage", 5)

    def print_all_for_pin(self, pin_idx):

        if len(self.averages) == 0:
            print("ERROR: Average information missing for all pins")
            return

        if len(self.averages[pin_idx]) == 0:
            print("ERROR: No average data obtained for pin {0}".format(pin_idx))
            return

        for i in range(len(self.averages[pin_idx])):
            iteration_idx = self.averages[pin_idx][i][0]
            hold_times_0 = round(self.averages[pin_idx][i][1][0], 5)
            hold_times_1 = round(self.averages[pin_idx][i][1][1], 5)

            if self.averages[pin_idx][i][3] is not None:
                average = round(self.averages[pin_idx][i][3], 6)
            else:
                average = "ignored"

            # '{message:{fill}{align}{width}}'.format(
            #     message='Hi',
            #     fill=' ',
            #     align='<',
            #     width=16,
            # )
            interval_duration = round(hold_times_1 - hold_times_0, 5)

            print("{0: >5}: ({1: >10} s, {2: >10} s) = {3: >10} s {4: >15} mC".format(iteration_idx, hold_times_0, hold_times_1, interval_duration, average))

        print("Total average charge: {0} mC".format(round(self.total_average[pin_idx], 6)))
        print("Total average current: {0} mA".format(round(self.total_average[pin_idx] / self.total_duration[pin_idx], 6)))
        print("Total time: {0} s".format(round(self.total_duration[pin_idx], 6)))
        print("Total energy: {0} mJ".format(round(self.total_average[pin_idx]*self.voltage, 6)))

    def calculate_all_for_pin(self, pin_idx, data = None, ignore_first_average = True):
        if data is None:
            data = self.dgilib_extra.data

        if len(self.averages) == 0 or len(self.averages[pin_idx]) == 0:
            return

        for i in range(len(self.averages[pin_idx])):
            iteration_idx = self.averages[pin_idx][i][0]
            hold_times = self.averages[pin_idx][i][1]
            start_index = self.averages[pin_idx][i][2]

            if ignore_first_average and i == 0:
                average = None
            else:
                average = calculate_average_leftpoint_single_interval(data.power, hold_times[0], hold_times[1], start_index)

            if average is not None:
                average_scaled = 1000 * average
                self.total_average[pin_idx] += average_scaled
                self.total_duration[pin_idx] += hold_times[1] - hold_times[0]
                self.total_iterations[pin_idx] += 1
            else:
                average_scaled = None
            self.averages[pin_idx][i] = (iteration_idx, hold_times, start_index, average_scaled)

        if len(self.averages[pin_idx]) > 0: 
            self.total_average[pin_idx] /= self.total_iterations[pin_idx]