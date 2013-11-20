'''
Created on 24 kwi 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import numpy as np
    from hra_core.units import get_time_unit
    from hra_math.model.data_vector import DataVector
    from hra_math.utils.array_utils import \
        get_max_index_for_cumulative_sum_greater_then_value
    from hra_math.utils.array_utils import \
        get_max_index_for_cumulative_sum_of_means_greater_then_value
except ImportError as error:
    print_import_error(__name__, error)


class SegmenterManager(object):

    @staticmethod
    def getDataVectorSegmenter(data, window_size,
                     window_size_unit=None, sample_step=None,
                     shift=1, stepper_size=None, stepper_unit=None,
                     mark_last_segment=False):

        if not stepper_size == None:
            return __SteppedDataVectorSegmenter__(data, window_size,
                                            window_size_unit,
                                            stepper_size, stepper_unit,
                                            shift, mark_last_segment)
        elif not sample_step == None:
            return __SampledDataVectorSegmenter__(data, window_size,
                                                window_size_unit,
                                                sample_step, shift,
                                                mark_last_segment)
        else:
            return __BitDataVectorSegmenter__(data, window_size,
                                              window_size_unit,
                                              shift, mark_last_segment)


class __DataVectorSegmenter__(object):

    def __init__(self, data, window_size, window_size_unit, shift=1,
                 mark_last_segment=False):
        self.data = data
        self.window_size = window_size
        self.window_size_unit = window_size_unit
        self.shift = shift
        self.__counter__ = 0
        self.__data_vector_segment__ = None
        self.__stop__ = False

        #None value of __last_segment__ means do not use last segment feature
        self.__last_segment__ = False if mark_last_segment else None

        self.window_unit = None

        if self.window_size_unit:
            #get time unit of window size
            self.window_unit = get_time_unit(self.window_size_unit)
            if not self.window_unit:
                raise Exception('Unknown window size unit !!! ['
                                + self.window_size_unit + ']')

        if self.window_unit:

            #calculate multiplier of conversion between data signal unit
            #and window size unit
            multiplier = self.window_unit.expressInUnit(self.data.signal_unit)
            self.window_size_in_signal_unit = multiplier * self.window_size
            if not self.data.time == None:
                #get an array of indexes where time period of an item is
                #greater than data window size, in this case further processing
                #is stopped
                indexes = np.where(self.data.time > self.window_size_in_signal_unit) # @IgnorePep8
                if len(indexes[0]) > 0:
                    #raise Exception('Window size is smaller then value in time column [in %s row] !' % (indexes[0][0])) # @IgnorePep8
                    print('Window size is smaller then value in time column [in %s row]. Stop processing !' % (indexes[0][0])) # @IgnorePep8
                    #mark to stop further processing
                    self.__stop__ = True
        else:
            if self.window_size > len(self.data.time_signal):
                raise Exception('Poincare window size greater then signal size !!!') #@IgnorePep8

        #optimization tricks, the methods below will not be searched in python
        #paths but access to them, because of below assignments, will be local
        #and for this reason much faster
        self.SEARCHSORTED = np.searchsorted
        self.ARANGE = np.arange

    def __iter__(self):
        return self

    def __getDataVactor__(self, index_start, index_stop):

        if self.stop:
            return

        if index_stop > self.signal_size:
            if not self.__last_segment__ == None:
                self.__last_segment__ = True
                return
            else:
                raise StopIteration

        indexes = self.ARANGE(index_start, index_stop + 1)
        signal = self.data.signal.take(indexes)

        indexes_plus = self.ARANGE(0, len(signal) - self.shift)
        signal_plus = signal.take(indexes_plus)

        indexes_minus = self.ARANGE(self.shift, len(signal))
        signal_minus = signal.take(indexes_minus)

        annotation = (None if self.data.annotation == None else
                      self.data.annotation.take(indexes))

        self.__counter__ += 1

        self.__data_vector_segment__ = DataVector(signal=signal,
                          signal_plus=signal_plus,
                          signal_minus=signal_minus,
                          annotation=annotation,
                          signal_unit=self.data.signal_unit,
                          signal_header=self.data.signal_header,
                          annotation_header=self.data.annotation_header,
                          time_header=self.data.time_header)
        return self.__data_vector_segment__

    @property
    def ordinal_value(self):
        return self.__counter__ + 1

    @property
    def data_changed(self):
        """
        method which returns True if data is changed otherwise False
        """
        return True

    @property
    def data(self):
        return self.__data__

    @data.setter
    def data(self, _data):
        self.__data__ = _data

    @property
    def signal_size(self):
        return len(self.data.signal)

    @property
    def shift(self):
        return self.__shift__

    @shift.setter
    def shift(self, _shift):
        self.__shift__ = _shift

    @property
    def window_size_unit(self):
        return self.__window_size_unit__

    @window_size_unit.setter
    def window_size_unit(self, _window_size_unit):
        self.__window_size_unit__ = _window_size_unit

    @property
    def window_unit(self):
        return self.__window_unit__

    @window_unit.setter
    def window_unit(self, _window_unit):
        self.__window_unit__ = _window_unit

    @property
    def window_size(self):
        return self.__window_size__

    @window_size.setter
    def window_size(self, _window_size):
        self.__window_size__ = _window_size

    @property
    def window_size_in_signal_unit(self):
        return self.__window_size_in_signal_unit__

    @window_size_in_signal_unit.setter
    def window_size_in_signal_unit(self, _window_size_in_signal_unit):
        self.__window_size_in_signal_unit__ = _window_size_in_signal_unit

    @property
    def data_vector_segment(self):
        return self.__data_vector_segment__

    @property
    def last_segment(self):
        return self.__last_segment__

    @last_segment.setter
    def last_segment(self, _last_segment):
        self.__last_segment__ = _last_segment

    @property
    def stop(self):
        return self.__stop__


class __BitDataVectorSegmenter__(__DataVectorSegmenter__):

    """
    class used to calculate segments of data vector based on number of bits
    """
    def __init__(self, data, window_size, window_size_unit, shift,
                 mark_last_segment=False):
        super(__BitDataVectorSegmenter__, self).__init__(data, window_size,
                                                         window_size_unit,
                                                         shift,
                                                         mark_last_segment)
        self.__index__ = 0

    def next(self):
        if self.stop:
            raise StopIteration

        #this means a user expressed window size in a unit
        if self.window_size_unit:
            max_index = get_max_index_for_cumulative_sum_greater_then_value(
                                            self.data.time_signal,
                                            self.window_size_in_signal_unit,
                                            self.__index__)
            if max_index == -1:
                if not self.last_segment == None:
                    self.last_segment = True
                    return
                else:
                    raise StopIteration

            #a new window size is a difference between max_index
            #and current index
            window_size = max_index - self.__index__
        else:
            window_size = self.window_size

        index_start = self.__index__
        index_stop = index_start + window_size

        self.__index__ += 1

        if index_stop < self.signal_size:
            return self.__getDataVactor__(index_start, index_stop)
        else:
            if not self.last_segment == None:
                self.last_segment = True
            else:
                raise StopIteration

    def segment_count(self):
        """
        the method calculates number of segments, if a window size is put in
        time units then the number of segments is an approximated value
        to avoid costly (in time) calculations
        """
        if self.window_size_unit:
            window_size = get_max_index_for_cumulative_sum_of_means_greater_then_value(  # @IgnorePep8
                                            self.data.time_signal,
                                            self.window_size_in_signal_unit)
        else:
            window_size = self.window_size
        return ((self.signal_size - window_size) / self.shift) + 1 \
                if window_size > 0 else window_size


class __SampledDataVectorSegmenter__(__DataVectorSegmenter__):

    """
    class used to calculate segments of data vector based on sample step
    """
    def __init__(self, data, window_size, window_size_unit, sample_step, shift,
                 mark_last_segment=False):
        super(__SampledDataVectorSegmenter__, self).__init__(data, window_size,
                                                             window_size_unit,
                                                             shift,
                                                             mark_last_segment)

        if not self.window_size_unit: # @IgnorePep8
            raise Exception('For window resampling step a window size unit is required !!!') # @IgnorePep8

        self.__sampled_data__ = np.arange(0, np.sum(self.data.time_signal),
                                sample_step)
        self.__sampled_signal_size__ = len(self.__sampled_data__)
        self.__cumsum_data__ = np.cumsum(self.data.time_signal)
        self.__sampled_window_size__ = self.window_size_in_signal_unit / sample_step # @IgnorePep8

        self.__index__ = 0
        self.__index_start_old__ = -1
        self.__index_stop_old__ = -1
        self.__data_segment_old__ = None

    def next(self):
        if self.stop:
            raise StopIteration

        self.__data_changed__ = True

        if self.__index__ + self.__sampled_window_size__ <= self.__sampled_signal_size__: # @IgnorePep8
            index_start = self.SEARCHSORTED(self.__cumsum_data__,
                                self.__sampled_data__[self.__index__])
            index_stop = self.SEARCHSORTED(self.__cumsum_data__,
                        self.__sampled_data__[
                            self.__index__ + self.__sampled_window_size__ - 1])

            self.__index__ += 1

            if self.__index_start_old__ == index_start \
                and self.__index_stop_old__ == index_stop:
                self.__data_changed__ = False
                return self.__data_segment_old__

            data_segment = self.__getDataVactor__(index_start, index_stop)

            self.__data_segment_old__ = data_segment
            self.__index_start_old__ = index_start
            self.__index_stop_old__ = index_stop

            return data_segment
        else:
            if not self.last_segment == None:
                self.last_segment = True
            else:
                raise StopIteration

    def segment_count(self):
        """
        a method calculates number of segments
        """
        size = self.__sampled_window_size__
        return self.__sampled_signal_size__ - size + 1 if size > 0 else size

    @property
    def data_changed(self):
        """
        method which returns True if data is changed otherwise False
        """
        return self.__data_changed__


class __SteppedDataVectorSegmenter__(__DataVectorSegmenter__):

    """
    class used to calculate segments of data vector based on
    value of stepping size
    """
    def __init__(self, data, window_size, window_size_unit,
                 stepper_size, stepper_unit, shift, mark_last_segment=False):
        super(__SteppedDataVectorSegmenter__, self).__init__(data, window_size,
                                                             window_size_unit,
                                                             shift,
                                                             mark_last_segment)

        self.__stepper_size__ = stepper_size

        #a flag which marks that a stepper is a simple bit's stepper
        self.__bits_stepper__ = False

        if (not self.window_size_unit == None and stepper_unit == None) \
            or (self.window_size_unit == None and not stepper_unit == None):
            raise Exception('Window size and stepper size must have both a unit or be without a unit !!!') # @IgnorePep8

        if stepper_unit:
            step_unit = get_time_unit(stepper_unit)
            if not step_unit:
                raise Exception('Unknown stepper size unit !!! [%s]' % stepper_unit)  # @IgnorePep8
            multiplier = step_unit.expressInUnit(self.data.signal_unit)
            self.__step_size_in_signal_unit__ = multiplier * self.__stepper_size__ # @IgnorePep8
        else:
            self.__step_size_in_signal_unit__ = self.__stepper_size__

        sum_signal = np.sum(self.data.time_signal)
        if self.__step_size_in_signal_unit__ > sum_signal:
            raise Exception('The step size is greater then the signal size !!!') # @IgnorePep8

        if self.window_size_unit == None and stepper_unit == None:
            #this means very simple situation when a signal is divided by
            #self.window_size number bits and for this reason
            #stepped signal size is the same as the signal size itself
            self.__stepped_signal_size__ = self.signal_size
            self.__bits_stepper__ = True
        else:
            #this creates a list of increased values which differ by
            #self.__step_size_in_signal_unit__ value
            #or in other words this is a partition of interval of sum_signal
            #length by a segment of self.__step_size_in_signal_unit__ length
            self.__stepped_data__ = np.arange(0, sum_signal,
                                          self.__step_size_in_signal_unit__)

            self.__stepped_signal_size__ = len(self.__stepped_data__)
            self.__cumsum_data__ = np.cumsum(self.data.time_signal)

        self.__stepper_index__ = 0
        self.__index_stop_old__ = None

    def next(self):
        if self.stop:
            raise StopIteration

        if self.__stepper_index__ < self.__stepped_signal_size__:
            if self.__stepper_index__ == 0:
                index_start = 0
            else:
                if self.__bits_stepper__:
                    index_start = self.__stepper_index__ + 1
                else:
                    #to avoid overlapping with previous index_stop
                    #one have to add plus 1 index
                    index_start = self.SEARCHSORTED(self.__cumsum_data__,
                            self.__stepped_data__[self.__stepper_index__]) + 1

            if self.__bits_stepper__:
                #this means simple division a signal by a number
                #self.window_size bits, for this reason index_stop
                #jumps by self.window_size bits
                index_stop = self.__stepper_index__ + self.window_size
            else:
                #index_stop ends where the window size ends
                index_stop = self.SEARCHSORTED(self.__cumsum_data__,
                        self.__stepped_data__[self.__stepper_index__] +
                                    self.window_size_in_signal_unit)

            if index_stop > self.signal_size:
                if not self.last_segment == None:
                    self.last_segment = True
                    return
                else:
                    raise StopIteration

            if index_stop == self.signal_size:
                index_stop = self.signal_size - 1
                if index_start > index_stop:
                    if not self.last_segment == None:
                        self.last_segment = True
                        return
                    else:
                        raise StopIteration

            if self.__bits_stepper__:
                #for simple bit's stepper index jumps by
                #__stepper_size__ quantity
                self.__stepper_index__ = self.__stepper_index__ + self.__stepper_size__ # @IgnorePep8
            else:
                #this index changes only by 1 because self.__stepped_data__
                #array, which is used in this case, contains an series of
                #increasing values which differ by self.__stepper_size__
                self.__stepper_index__ = self.__stepper_index__ + 1

                #test if segments of signals (current and previous)
                #do not overlap
                if not self.__index_stop_old__ == None:
                    if not (self.__index_stop_old__ + 1 == index_start):
                        raise Exception(
                        'Index error index_stop_old %s index_start %s !!!'
                                    % (self.__index_stop_old__, index_start))
                self.__index_stop_old__ = index_stop

            data_vector = self.__getDataVactor__(index_start, index_stop)

            #test if the last signal is included in window size signal
            if self.__stepper_index__ == len(self.__stepped_data__):
                if np.sum(data_vector.time_signal) < self.window_size_in_signal_unit: # @IgnorePep8
                    if not self.last_segment == None:
                        self.last_segment = True
                        return
                    else:
                        raise StopIteration

            return data_vector
        else:
            if not self.last_segment == None:
                self.last_segment = True
            else:
                raise StopIteration

    def segment_count(self):
        """
        a method calculates number of segments
        """
        if self.__bits_stepper__:
            return int((1.0 * self.signal_size / self.__stepper_size__))
        else:
            return self.__stepped_signal_size__
