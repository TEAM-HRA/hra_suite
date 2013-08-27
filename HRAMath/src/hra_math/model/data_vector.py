'''
Created on 24 kwi 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import pylab as pl
    from hra_core.misc import Params
    from hra_core.units import Millisecond
    from hra_math.utils.array_utils import array_copy
    from hra_math.model.utils import EMPTY_ARRAY
except ImportError as error:
    print_import_error(__name__, error)


class DataVector(object):

    def __init__(self, **params):
        '''
        Constructor
        '''
        self.__params__ = Params(**params)
        if self.__params__.signal_unit is None:
            self.__params__.signal_unit = Millisecond

    @property
    def signal(self):
        return self.__params__.signal

    @signal.setter
    def signal(self, _signal):
        self.__params__.signal = _signal

    @property
    def annotation(self):
        return self.__params__.annotation

    @annotation.setter
    def annotation(self, _annotation):
        self.__params__.annotation = _annotation

    @property
    def time(self):
        return self.__params__.time

    @time.setter
    def time(self, _time):
        self.__params__.time = _time

    @property
    def signal_plus(self):
        return self.__params__.signal_plus

    @signal_plus.setter
    def signal_plus(self, _signal_plus):
        self.__params__.signal_plus = _signal_plus

    @property
    def signal_minus(self):
        return self.__params__.signal_minus

    @signal_minus.setter
    def signal_minus(self, _signal_minus):
        self.__params__.signal_minus = _signal_minus

    @property
    def signal_unit(self):
        return self.__params__.signal_unit

    @signal_unit.setter
    def signal_unit(self, _signal_unit):
        self.__params__.signal_unit = _signal_unit

    @property
    def data(self):
        pass

    @data.setter
    def data(self, _data):
        self.__params__ = Params(signal=_data.signal,
                                 signal_plus=_data.signal_plus,
                                 signal_minus=_data.signal_minus,
                                 annotation=_data.annotation,
                                 signal_unit=_data.signal_unit,
                                 time=_data.time,
                                 signal_header=_data.signal_header,
                                 annotation_header=_data.annotation_header,
                                 time_header=_data.time_header)
        #raise Exception('Parameter data have to be of DataSource type !!!')

    def __str__(self):
        return (' '.join(
            [self.__for_str__('signal', self.__params__.signal),
             self.__for_str__('signal_plus', self.__params__.signal_plus),
             self.__for_str__('signal_minus', self.__params__.signal_minus),
             self.__for_str__('annotation', self.__params__.annotation),
             self.__for_str__('time', self.__params__.time)]))

    def __for_str__(self, prefix, data):
        if hasattr(data, 'take') or hasattr(data, '__getslice__'):
            l = len(data)
            if hasattr(data, 'take'):
                sample = data.take(range(10 if l > 10 else l))
            elif hasattr(data, '__getslice__'):
                sample = data[0:(10 if l > 10 else l)]
            return ("{0} [size {1} sample {2}] ".format(prefix, l, sample))
        return ''

    # if parameter is not set in the __init__() method then returns None
    def __getattr__(self, name):
        return None

    def copy(self):
        """
        create copy of this DataVector object
        """
        return DataVector(
            signal=array_copy(self.signal),
            signal_plus=array_copy(self.signal_plus),
            signal_minus=array_copy(self.signal_minus),
            annotation=array_copy(self.annotation),
            signal_unit=self.signal_unit,
            time=array_copy(self.time),
            signal_header=self.signal_header,
            annotation_header=self.annotation_header,
            time_header=self.time_header)

    @property
    def signal_header(self):
        return self.__params__.signal_header

    @signal_header.setter
    def signal_header(self, _signal_header):
        self.__params__.signal_header = _signal_header

    @property
    def annotation_header(self):
        return self.__params__.annotation_header

    @annotation_header.setter
    def annotation_header(self, _annotation_header):
        self.__params__.annotation_header = _annotation_header

    @property
    def time_header(self):
        return self.__params__.annotation_header

    @time_header.setter
    def time_header(self, _time_header):
        self.__params__.time_header = _time_header

    def equals(self, other_data_vector):
        """
        method check equality of other data vector with itself
        based only on equality of signal_plus
        """
        if not self.signal_plus == None and not other_data_vector == None:
            #there is only check of one element - signal_plus array
            return pl.array_equal(self.signal_plus,
                                  other_data_vector.signal_plus)
        return False


EMPTY_DATA_VECTOR = DataVector(signal=EMPTY_ARRAY, signal_plus=EMPTY_ARRAY,
                               signal_minus=EMPTY_ARRAY, time=EMPTY_ARRAY,
                               annotation=EMPTY_ARRAY, signal_unit=None,
                               signal_header=None, annotation_header=None,
                               time_header=None)
