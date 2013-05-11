'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import numpy as np
    from pycore.units import get_time_unit
    from pymath.model.data_vector import DataVector
    from pymath.utils.array_utils import \
        get_max_index_for_cumulative_sum_greater_then_value
    from pymath.utils.array_utils import \
        get_max_index_for_cumulative_sum_of_means_greater_then_value
except ImportError as error:
    print_import_error(__name__, error)


class DataVectorSegmenter(object):

    def __init__(self, data, window_size,  shift=1, window_size_unit=None):
        self.__data__ = data
        self.__window_size__ = window_size
        self.__shift__ = shift
        self.__index__ = 0
        self.__window_size_unit__ = window_size_unit
        self.__window_unit__ = None

        #this means a user put window size in some unit
        if self.__window_size_unit__:
            #get time unit of window size
            self.__window_unit__ = get_time_unit(self.__window_size_unit__)

            #convert signal unit into window size unit,
            #for example express milliseconds in minutes
            multiplier = self.__window_unit__.expressInUnit(
                                                    self.__data__.signal_unit)

            #express window size in units of a signal
            self.__window_size__ = multiplier * window_size
        else:
            if self.__window_size__ > len(self.__data__.signal):
                raise Exception('Poincare window size greater then signal size !!!') #@IgnorePep8

    def __iter__(self):
        return self

    def next(self):
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
            indexes = np.arange(self.__index__, self.__index__ + signal_size)
            signal = self.__data__.signal.take(indexes)

            indexes_plus = np.arange(self.__index__,
                                 self.__index__ + signal_size - self.__shift__)
            signal_plus = self.__data__.signal.take(indexes_plus)

            indexes_minus = np.arange(self.__index__ + self.__shift__,
                                  self.__index__ + signal_size)
            signal_minus = self.__data__.signal.take(indexes_minus)

            annotation = (None if self.__data__.annotation == None else
                          self.__data__.annotation.take(indexes))

            self.__index__ += self.__shift__

            return DataVector(signal=signal,
                              signal_plus=signal_plus,
                              signal_minus=signal_minus,
                              annotation=annotation,
                              signal_unit=self.__data__.signal_unit)
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
