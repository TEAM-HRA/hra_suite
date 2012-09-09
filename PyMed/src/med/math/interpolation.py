'''
Created on 03-09-2012

@author: jurek
'''

from numpy import mean
from pylab import find
from pylab import arange

from med.data_sources.datasources import DataSource


class Interpolation(DataSource):
    def __init__(self):
        pass

    def interpolate(self):
        if not self.signal == None and not self.annotation == None:
            return self.__interpolate__(self.signal, self.annotation)

    def __interpolate__(self, signal, annotation):
        return None


class LinearInterpolation(Interpolation):
    def __interpolate__(self, _signal, _annotation):
        #removing nonsinus beats from the beginning
        while _annotation[0] != 0:
            _signal = _signal[1:-1]
            _annotation = _annotation[1:-1]
        #removing nonsinus beats from the end
        while _annotation[-1] != 0:
            _signal = _signal[0:-2]
            _annotation = _annotation[0:-2]
        index_nonsin = find(_annotation != 0)
        krok = 1
        for i in arange(0, len(index_nonsin)):
            if i + 1 <= (len(index_nonsin) - 1) and (index_nonsin[i + 1]
                                                     - index_nonsin[i]) == 1:
                krok += 1
            else:
                delta = (_signal[index_nonsin[i] + 1]
                         - _signal[index_nonsin[i] - krok]) / (krok + 1)
                for k in arange(1, krok + 1):
                    _signal[index_nonsin[i] - krok + k] = _signal[index_nonsin[i] #@IgnorePep8
                                                         - krok] + delta * k
                krok += 1
        return _signal


class MeanInterpolation(Interpolation):
    def __interpolate__(self, _signal, _annotation):
        sinus_index = find(_annotation == 0)
        nonsinus_index = find(_annotation != 0)
        mean_sinus = mean(_signal[sinus_index])
        _signal[nonsinus_index] = mean_sinus
        return _signal
