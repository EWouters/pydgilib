from pydgilib_extra.dgilib_calculations import HoldTimes
from pydgilib_extra.dgilib_calculations import calculate_average

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

            average = round(self.averages[pin_idx][i][3], 6)

            # '{message:{fill}{align}{width}}'.format(
            #     message='Hi',
            #     fill=' ',
            #     align='<',
            #     width=16,
            # )
            interval_duration = round(hold_times_1 - hold_times_0, 5)
            print("{0: >5}: ({1: >10} s, {2: >10} s) = {3: >10} s {4: >15} mC".format(iteration_idx, hold_times_0, hold_times_1, interval_duration, average))

        print("Total average: {0} mC".format(round(self.total_average[pin_idx], 6)))
        print("Total time while pin {0} was holding: {1} s".format(pin_idx, round(self.total_duration[pin_idx], 6)))

    def calculate_all_for_pin(self, pin_idx, data = None):
        if data is None:
            data = self.dgilib_extra.data

        if len(self.averages) == 0 or len(self.averages[pin_idx]) == 0:
            return

        for i in range(len(self.averages[pin_idx])):
            iteration_idx = self.averages[pin_idx][i][0]
            hold_times = self.averages[pin_idx][i][1]
            start_index = self.averages[pin_idx][i][2]

            average = calculate_average(data.power, hold_times[0], hold_times[1], start_index)

            if average is not None:
                average_scaled = 1000 * average
            else:
                average_scaled = -1
            self.averages[pin_idx][i] = (iteration_idx, hold_times, start_index, average_scaled)

            self.total_average[pin_idx] += average_scaled
            self.total_duration[pin_idx] += hold_times[1] - hold_times[0]

        if len(self.averages[pin_idx]) > 0: 
            self.total_average[pin_idx] /= len(self.averages[pin_idx]) #self.iterations[pin_idx]