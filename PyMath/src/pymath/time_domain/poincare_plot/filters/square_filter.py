'''
Created on 9 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import pylab as pl
    from pycore.collections_utils import nvl
    from pycore.collections_utils import is_empty
    from pycore.misc import Params
    from pycore.units import Millisecond
    from pymath.datasources import DataVector
    from pymath.time_domain.poincare_plot.filters.filter_utils import Filter
except ImportError as error:
    print_import_error(__name__, error)

DEFAULT_MIN_VALUE = 300
DEFAULT_MAX_VALUE = 2000


class SquareFilter(Filter):
    """
    square filter
    """
    def __init__(self, shift=1, **params):
        super(SquareFilter, self).__init__(shift=shift)
        params = Params(**params)
        self.min_value = nvl(params.min_value, DEFAULT_MIN_VALUE)
        self.max_value = nvl(params.max_value, DEFAULT_MAX_VALUE)
        self.__value_unit__ = Millisecond

    def check(self, _data_vector=None):
        if self.min_value > self.max_value:
            return "Min value has to be smaller or equal to max value !"

    def __filter__(self, _data_vector):

        indexes = pl.find(
            pl.logical_and(_data_vector.signal >= self.min_value,
                           _data_vector.signal <= self.max_value))
        if len(indexes) == len(_data_vector.signal):  # nothing change
            return _data_vector
        else:
            signal = _data_vector.signal[indexes]
            annotation = _data_vector.annotation[indexes]
            signal_plus = signal[pl.arange(0, len(signal) - self.__shift__)]
            signal_minus = signal[pl.arange(self.__shift__, len(signal))]
            time = _data_vector.time[indexes] if _data_vector.time else None
            return DataVector(signal=signal, signal_plus=signal_plus,
                          signal_minus=signal_minus,
                          time=time, annotation=annotation,
                          signal_unit=_data_vector.signal_unit)

    @property
    def min_value(self):
        return self.__min_value__

    @min_value.setter
    def min_value(self, _min_value):
        if isinstance(_min_value, int):
            self.__min_value__ = _min_value
        else:
            self.__min_value__ = 0 if is_empty(_min_value) else int(_min_value)

    @property
    def max_value(self):
        return self.__max_value__

    @max_value.setter
    def max_value(self, _max_value):
        if isinstance(_max_value, int):
            self.__max_value__ = _max_value
        else:
            self.__max_value__ = 0 if is_empty(_max_value) else int(_max_value)

    def reset(self, _min=None, _max=None):
        self.min_value = nvl(_min, DEFAULT_MIN_VALUE)
        self.max_value = nvl(_max, DEFAULT_MAX_VALUE)
