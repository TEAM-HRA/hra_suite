'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import numpy as np
    from pycore.units import get_time_unit
    from pymath.statistics.statistics import MeanStatistic
    from pymath.model.data_vector import DataVector
    from pymath.utils.array_utils import \
        get_max_index_for_cumulative_sum_greater_then_value
    from pymath.utils.array_utils import \
        get_max_index_for_cumulative_sum_of_means_greater_then_value
except ImportError as error:
    print_import_error(__name__, error)


class DataVectorSegmenter(object):

    def __init__(self, data, window_size,  shift=1, window_size_unit=None,
                 filter_manager=None, normalize_window_size=True):
        self.__data__ = data
        self.__shift__ = shift
        self.__index__ = 0
        self.__window_unit__ = None

        self.__index_start_old__ = -1
        self.__index_stop_old__ = -1
        self.__data_segment_old__ = None

        self.__calculate_window_size__(window_size, window_size_unit,
                                       normalize_window_size, filter_manager)

    def __iter__(self):
        return self

    def next(self):
        self.__data_changed__ = True
        #this means a user expresses window size in a unit
        if self.__window_size_unit__:
            max_index = get_max_index_for_cumulative_sum_greater_then_value(
                                                self.__data__.signal,
                                                self.__window_size__,
                                                self.__index__)
            if max_index == -1:
                raise StopIteration

            #new window size is a difference between max_index a start index
            signal_size = max_index - self.__index__
        else:
            signal_size = self.__window_size__
        if self.__index__ + signal_size <= len(self.__data__.signal):

            index_start = self.__index__
            self.__index__ += self.__shift__
            index_stop = index_start + signal_size
            if self.__index_start_old__ == index_start \
                and self.__index_stop_old__ == index_stop:
                self.__data_changed__ = False
                return self.__data_segment_old__
            self.__index_start_old__ = index_start
            self.__index_stop_old__ = index_stop

            shift = self.__shift__

            signal = self.__data__.signal[index_start:index_stop]
            signal_plus = self.__data__.signal[index_start:index_stop - shift]
            signal_minus = self.__data__.signal[index_start + shift:index_stop]

            annotation = (None if self.__data__.annotation == None else
                          self.__data__.annotation[index_start:index_stop])

            self.__data_segment__ = DataVector(signal=signal,
                              signal_plus=signal_plus,
                              signal_minus=signal_minus,
                              annotation=annotation,
                              signal_unit=self.__data__.signal_unit)
            self.__data_segment_old__ = self.__data_segment__
            return self.__data_segment__
        else:
            raise StopIteration

    @property
    def data_index(self):
        #self.__shift have to be subtracted because it was added in next()
        #method
        return self.__index__ - self.__shift__

    @property
    def ordinal_value(self):
        if self.__window_size_unit__:
            multiplier = self.__data__.signal_unit.expressInUnit(
                                                    self.__window_unit__)
            return multiplier * np.sum(self.__data__.signal[:self.data_index])
        else:
            return self.data_index

    def segment_count(self):
        """
        the method calculates number of segments, if a window size is put in
        time units a number of segments is an approximation value to avoid
        costly (in time) calculations
        """
        if self.__window_size_unit__:
            size = get_max_index_for_cumulative_sum_of_means_greater_then_value(  # @IgnorePep8
                                                    self.__data__.signal,
                                                    self.__window_size__)
        else:
            size = self.__window_size__
        return ((len(self.__data__.signal) - size) / self.__shift__) + 1 \
                if size > 0 else size

    def __calculate_window_size__(self, window_size, window_size_unit,
                                  normalize_window_size, filter_manager):
        """
        method calculates correct window size
        """
        self.__window_size_unit__ = window_size_unit
        self.__window_size__ = window_size
        data = self.__data__
        if self.__window_size__:

            #get time unit of window size
            self.__window_unit__ = get_time_unit(self.__window_size_unit__)
            if not self.__window_unit__:
                raise Exception('Unknown window size unit !!! ['
                                + self.__window_unit__ + ']')

            #calculate multiplier of conversion between data signal unit
            #and window size unit
            multiplier = self.__window_unit__.expressInUnit(data.signal_unit)
            window_size_in_signal_unit = multiplier * window_size

            #express window size put in some unit in normalized
            #number of data, normalized means calculate a mean of a signal
            #(filtered signal if required) and calculate how many means
            #divide the whole window size
            if normalize_window_size:
                if filter_manager:
                    data = filter_manager.run_filters(data)

                mean_stat = MeanStatistic()
                mean_stat.data = data
                mean_signal = mean_stat.compute()

                #number of means per window_size_in_signal_unit
                window_size_in_signal_unit = int(
                                    window_size_in_signal_unit / mean_signal)
                #because window size is expressed in number of data points,
                #window size unit is not required any more
                self.__window_size_unit__ = None
                print('Using normalized window size: ' +
                                            str(window_size_in_signal_unit))

            self.__window_size__ = window_size_in_signal_unit
        else:
            if self.__window_size__ > len(data.signal):
                raise Exception('Poincare window size greater then signal size !!!') #@IgnorePep8

    def data_changed(self):
        """
        method which returns True if data is changed otherwise False
        """
        return self.__data_changed__
