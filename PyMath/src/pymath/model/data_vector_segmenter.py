'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import numpy as np
    from pycore.collections_utils import nvl
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
                 filter_manager=None, normalize_window_size=True,
                 window_resampling_step=None):
        self.__data__ = data
        self.__shift__ = shift
        self.__index__ = 0
        self.__window_unit__ = None
        self.__signal_size__ = len(self.__data__.signal)

        self.__index_start_old__ = -1
        self.__index_stop_old__ = -1
        self.__data_segment_old__ = None
        # 0 value means no resampling
        self.__window_resampling_step__ = nvl(window_resampling_step, 0)

        self.__calculate_window_size__(window_size, window_size_unit,
                                       normalize_window_size, filter_manager)

        #optimization tricks, the methods below will not be searched in python
        #paths but access to them, because of below assignments, will be local
        #and for this reason much faster
        self.SEARCHSORTED = np.searchsorted
        self.ARANGE = np.arange

    def __iter__(self):
        return self

    def next(self):
        self.__data_changed__ = True

        if self.__window_resampling_step__ > 0:
            return self.__resampled_next__()

        #this means a user expresses window size in a unit
        elif self.__window_size_unit__:
            max_index = get_max_index_for_cumulative_sum_greater_then_value(
                                                self.__data__.signal,
                                                self.__window_size__,
                                                self.__index__)
            if max_index == -1:
                raise StopIteration

            #new window size is a difference between max_index a start index
            window_size = max_index - self.__index__
        else:
            window_size = self.__window_size__

        if self.__index__ + window_size <= self.__signal_size__:

            index_start = self.__index__
            index_stop = index_start + window_size

            self.__index__ += 1

            shift = self.__shift__

            indexes = self.ARANGE(index_start, index_stop + 1)
            signal = self.__data__.signal.take(indexes)

            indexes_plus = self.ARANGE(0, len(signal) - shift)
            signal_plus = signal.take(indexes_plus)

            indexes_minus = self.ARANGE(shift, len(signal))
            signal_minus = signal.take(indexes_minus)

            annotation = (None if self.__data__.annotation == None else
                          self.__data__.annotation.take(indexes))

            return DataVector(signal=signal,
                              signal_plus=signal_plus,
                              signal_minus=signal_minus,
                              annotation=annotation,
                              signal_unit=self.__data__.signal_unit)
        else:
            raise StopIteration

    def __resampled_next__(self):

        if self.__index__ + self.__resampled_window_size__ > self.__signal_size__ - self.__shift__: # @IgnorePep8
            raise StopIteration

        index_start = self.SEARCHSORTED(self.__cumsum_data__,
                                    self.__resampled_data__[self.__index__])
        index_stop = self.SEARCHSORTED(self.__cumsum_data__,
                                       self.__resampled_data__[self.__index__ +
                                            self.__resampled_window_size__])

        if self.__index__ + self.__resampled_window_size__ < self.__signal_size__: # @IgnorePep8

            self.__index__ += 1

            if self.__index_start_old__ == index_start \
                and self.__index_stop_old__ == index_stop:
                self.__data_changed__ = False
                return self.__data_segment_old__

            shift = self.__shift__

            indexes = self.ARANGE(index_start, index_stop + 1)
            signal = self.__data__.signal.take(indexes)

            indexes_plus = self.ARANGE(0, len(signal) - shift)
            signal_plus = signal.take(indexes_plus)

            indexes_minus = self.ARANGE(shift, len(signal))
            signal_minus = signal.take(indexes_minus)

            annotation = (None if self.__data__.annotation == None else
                          self.__data__.annotation.take(indexes))

            self.__data_segment__ = DataVector(signal=signal,
                                    signal_plus=signal_plus,
                                    signal_minus=signal_minus,
                                    annotation=annotation,
                                    signal_unit=self.__data__.signal_unit)
            self.__data_segment_old__ = self.__data_segment__
            self.__index_start_old__ = index_start
            self.__index_stop_old__ = index_stop

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
        if self.__window_resampling_step__ > 0:
            window_size = self.__resampled_window_size__
            signal_size = self.__signal_size__
        elif self.__window_size_unit__:
            window_size = get_max_index_for_cumulative_sum_of_means_greater_then_value(  # @IgnorePep8
                                                    self.__data__.signal,
                                                    self.__window_size__)
            signal_size = self.__signal_size__
        else:
            window_size = self.__window_size__
            signal_size = self.__signal_size__
        return ((signal_size - window_size) / self.__shift__) + 1 \
                if window_size > 0 else window_size

    def __calculate_window_size__(self, window_size, window_size_unit,
                                  normalize_window_size, filter_manager):
        """
        method calculates correct window size
        """
        self.__window_size_unit__ = window_size_unit
        self.__window_size__ = window_size
        data = self.__data__

        if self.__window_resampling_step__ > 0 and not self.__window_size_unit__: # @IgnorePep8
            raise Exception('For window resampling step a window size unit is required !!!') # @IgnorePep8

        if self.__window_size_unit__:

            #get time unit of window size
            self.__window_unit__ = get_time_unit(self.__window_size_unit__)
            if not self.__window_unit__:
                raise Exception('Unknown window size unit !!! ['
                                + self.__window_unit__ + ']')

            #calculate multiplier of conversion between data signal unit
            #and window size unit
            multiplier = self.__window_unit__.expressInUnit(data.signal_unit)
            window_size_in_signal_unit = multiplier * window_size

            if self.__window_resampling_step__ > 0:
                self.__resampled_data__ = np.arange(0,
                                            np.sum(self.__data__.signal),
                                            self.__window_resampling_step__)
                self.__signal_size__ = len(self.__resampled_data__)
                self.__cumsum_data__ = np.cumsum(self.__data__.signal)
                self.__window_size__ = window_size_in_signal_unit
                self.__resampled_window_size__ = window_size_in_signal_unit / self.__window_resampling_step__ # @IgnorePep8

            #express window size put in some unit in normalized
            #number of data, normalized means calculate a mean of a signal
            #(filtered signal if required) and calculate how many means
            #divide the whole window size
            elif normalize_window_size:
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
                self.__window_size__ = window_size_in_signal_unit
                print('Using normalized window size: ' +
                                                    str(self.__window_size__))
            else:
                self.__window_size__ = window_size_in_signal_unit
        else:
            if self.__window_size__ > len(data.signal):
                raise Exception('Poincare window size greater then signal size !!!') #@IgnorePep8

    @property
    def data_changed(self):
        """
        method which returns True if data is changed otherwise False
        """
        return self.__data_changed__
